from fastapi import APIRouter, Depends, HTTPException, Query

from app.clients.openalex import OpenAlexClient, OpenAlexUpstreamError, get_openalex_client
from app.core.config import settings
from app.models.schemas import DiscoveryResponse
from app.services.discovery import rank_authors

router = APIRouter(tags=["discovery"])


@router.get("/discovery", response_model=DiscoveryResponse)
async def discover_professors(
    topic: str = Query(..., min_length=2),
    institution_id: str = Query(..., min_length=2),
    offset: int = Query(0, ge=0),
    limit: int = Query(10, ge=1, le=settings.max_page_size),
    client: OpenAlexClient = Depends(get_openalex_client),
) -> DiscoveryResponse:
    try:
        works_payload = await client.search_works_by_topic_and_institution(
            topic=topic.strip(),
            institution_id=institution_id.strip(),
        )
    except OpenAlexUpstreamError as exc:
        raise HTTPException(status_code=502, detail="OpenAlex unavailable") from exc

    ranked_authors = rank_authors(
        topic=topic,
        institution_id=institution_id,
        works_payload=works_payload,
    )
    total = len(ranked_authors)
    paged = ranked_authors[offset : offset + limit]

    return DiscoveryResponse(
        query=topic,
        institution_id=institution_id,
        offset=offset,
        limit=limit,
        total=total,
        results=paged,
    )
