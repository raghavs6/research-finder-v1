import datetime as dt
import re
from dataclasses import dataclass, field

from app.core.config import settings
from app.models.schemas import DiscoveryAuthorResult, WorkItem


_TOKEN_PATTERN = re.compile(r"[a-z0-9]+")


def _normalize_tokens(text: str) -> set[str]:
    return set(_TOKEN_PATTERN.findall(text.lower()))


def _normalize_openalex_id(identifier: str | None) -> str:
    if not identifier:
        return ""
    return identifier.rsplit("/", maxsplit=1)[-1]


def reconstruct_abstract(abstract_inverted_index: dict | None) -> str:
    if not abstract_inverted_index:
        return ""

    positions: dict[int, str] = {}
    for word, indices in abstract_inverted_index.items():
        for idx in indices:
            positions[idx] = word

    return " ".join(token for _, token in sorted(positions.items(), key=lambda item: item[0]))


def relevance_score(topic: str, title: str, abstract: str) -> float:
    topic_tokens = _normalize_tokens(topic)
    if not topic_tokens:
        return 0.0

    work_tokens = _normalize_tokens(f"{title} {abstract}")
    overlap = topic_tokens.intersection(work_tokens)
    return len(overlap) / len(topic_tokens)


def recency_score(publication_year: int | None) -> float:
    if publication_year is None:
        return 0.0

    current_year = dt.datetime.utcnow().year
    age_years = max(0, current_year - publication_year)
    return 1.0 / (1.0 + age_years)


def _is_top_venue(venue: str | None) -> bool:
    if not venue:
        return False
    normalized = venue.strip().lower()
    return normalized in set(settings.top_venues)


@dataclass
class AuthorAccumulator:
    author_id: str
    author_name: str
    institution_name: str | None = None
    score: float = 0.0
    matching_works_count: int = 0
    recent_works_count: int = 0
    top_venue_works_count: int = 0
    top_works: list[tuple[float, WorkItem]] = field(default_factory=list)


def rank_authors(
    topic: str,
    institution_id: str,
    works_payload: dict,
) -> list[DiscoveryAuthorResult]:
    results = works_payload.get("results", [])
    accumulators: dict[str, AuthorAccumulator] = {}
    normalized_institution_id = _normalize_openalex_id(institution_id)

    current_year = dt.datetime.utcnow().year

    for work in results:
        title = work.get("display_name") or "Untitled"
        publication_year = work.get("publication_year")
        abstract = reconstruct_abstract(work.get("abstract_inverted_index"))
        venue = (
            work.get("primary_location", {})
            .get("source", {})
            .get("display_name")
        )

        relevance = relevance_score(topic, title, abstract)
        if relevance <= 0:
            continue

        recency = recency_score(publication_year)
        base_contribution = relevance * recency
        venue_bonus = 0.25 if _is_top_venue(venue) else 0.0
        contribution = base_contribution + venue_bonus

        work_item = WorkItem(
            work_id=work.get("id", ""),
            title=title,
            publication_year=publication_year,
            venue=venue,
            openalex_url=work.get("id"),
        )

        for authorship in work.get("authorships", []):
            author = authorship.get("author", {})
            author_id = author.get("id")
            author_name = author.get("display_name")
            if not author_id or not author_name:
                continue

            institutions = authorship.get("institutions", [])
            matches_institution = any(
                _normalize_openalex_id(inst.get("id")) == normalized_institution_id
                for inst in institutions
            )
            if not matches_institution:
                continue

            accumulator = accumulators.get(author_id)
            if accumulator is None:
                institution_name = next(
                    (
                        inst.get("display_name")
                        for inst in institutions
                        if _normalize_openalex_id(inst.get("id")) == normalized_institution_id
                    ),
                    None,
                )
                accumulator = AuthorAccumulator(
                    author_id=author_id,
                    author_name=author_name,
                    institution_name=institution_name,
                )
                accumulators[author_id] = accumulator

            accumulator.score += contribution
            accumulator.matching_works_count += 1
            if publication_year is not None and current_year - publication_year <= settings.recency_window_years:
                accumulator.recent_works_count += 1
            if venue_bonus > 0:
                accumulator.top_venue_works_count += 1
            accumulator.top_works.append((contribution, work_item))

    ranked = sorted(
        accumulators.values(),
        key=lambda item: (-item.score, -item.matching_works_count, item.author_name.lower()),
    )

    final: list[DiscoveryAuthorResult] = []
    for item in ranked:
        top_works = [
            work for _, work in sorted(item.top_works, key=lambda x: (-x[0], x[1].title.lower()))[: settings.top_works_per_author]
        ]
        final.append(
            DiscoveryAuthorResult(
                author_id=item.author_id,
                author_name=item.author_name,
                institution_name=item.institution_name,
                score=round(item.score, 4),
                matching_works_count=item.matching_works_count,
                recent_works_count=item.recent_works_count,
                top_venue_works_count=item.top_venue_works_count,
                top_works=top_works,
            )
        )

    return final
