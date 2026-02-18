import datetime as dt
from dataclasses import dataclass, field

from app.core.config import AREA_VENUE_KEYWORDS, settings
from app.models.schemas import DiscoveryAuthorResult, WorkItem


def _normalize_openalex_id(identifier: str | None) -> str:
    if not identifier:
        return ""
    return identifier.rsplit("/", maxsplit=1)[-1]


def recency_score(publication_year: int | None) -> float:
    if publication_year is None:
        return 0.0

    current_year = dt.datetime.utcnow().year
    age_years = max(0, current_year - publication_year)
    return 1.0 / (1.0 + age_years)


def _venue_matches_area(venue: str | None, keywords: tuple[str, ...]) -> bool:
    if not venue or not keywords:
        return False
    normalized = venue.strip().lower()
    return any(kw in normalized for kw in keywords)


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
    area: str,
    institution_id: str,
    works_payload: dict,
) -> list[DiscoveryAuthorResult]:
    keywords = AREA_VENUE_KEYWORDS.get(area, ())
    results = works_payload.get("results", [])
    accumulators: dict[str, AuthorAccumulator] = {}
    normalized_institution_id = _normalize_openalex_id(institution_id)

    current_year = dt.datetime.utcnow().year

    for work in results:
        if not isinstance(work, dict):
            continue

        title = work.get("display_name") or "Untitled"
        publication_year = work.get("publication_year")
        primary_location = work.get("primary_location")
        if not isinstance(primary_location, dict):
            primary_location = {}

        source = primary_location.get("source")
        if not isinstance(source, dict):
            source = {}

        venue_value = source.get("display_name")
        venue = venue_value if isinstance(venue_value, str) else None

        if not _venue_matches_area(venue, keywords):
            continue

        recency = recency_score(publication_year)
        contribution = recency

        work_item = WorkItem(
            work_id=work.get("id", ""),
            title=title,
            publication_year=publication_year,
            venue=venue,
            openalex_url=work.get("id"),
        )

        authorships = work.get("authorships")
        if not isinstance(authorships, list):
            authorships = []

        for authorship in authorships:
            if not isinstance(authorship, dict):
                continue

            author = authorship.get("author")
            if not isinstance(author, dict):
                continue

            author_id = author.get("id")
            author_name = author.get("display_name")
            if not author_id or not author_name:
                continue

            institutions = authorship.get("institutions")
            if not isinstance(institutions, list):
                institutions = []

            matches_institution = any(
                isinstance(inst, dict) and _normalize_openalex_id(inst.get("id")) == normalized_institution_id
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
            accumulator.top_venue_works_count += 1
            if publication_year is not None and current_year - publication_year <= settings.recency_window_years:
                accumulator.recent_works_count += 1
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
