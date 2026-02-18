from fastapi import APIRouter, Depends, HTTPException, Query

from app.clients.openalex import OpenAlexClient, OpenAlexUpstreamError, get_openalex_client
from app.core.config import AREA_CONFERENCES, settings
from app.models.schemas import DiscoveryResponse
from app.services.discovery import rank_authors

router = APIRouter(tags=["discovery"])


@router.get("/discovery", response_model=DiscoveryResponse)
async def discover_professors(
    area: str = Query(..., min_length=1),
    institution_id: str = Query(..., min_length=2),
    offset: int = Query(0, ge=0),
    limit: int = Query(10, ge=1, le=settings.max_page_size),
    client: OpenAlexClient = Depends(get_openalex_client),
) -> DiscoveryResponse:
    if area not in AREA_CONFERENCES:
        raise HTTPException(status_code=400, detail=f"Unknown area: {area!r}. Must be one of: {list(AREA_CONFERENCES)}")

    try:
        works_payload = await client.search_works_by_institution(
            institution_id=institution_id.strip(),
            per_page=200,
        )
    except OpenAlexUpstreamError as exc:
        raise HTTPException(status_code=502, detail="OpenAlex unavailable") from exc

    ranked_authors = rank_authors(
        area=area,
        institution_id=institution_id,
        works_payload=works_payload,
    )
    total = len(ranked_authors)
    paged = ranked_authors[offset : offset + limit]

    return DiscoveryResponse(
        area=area,
        institution_id=institution_id,
        offset=offset,
        limit=limit,
        total=total,
        results=paged,
    )
