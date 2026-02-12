from fastapi import APIRouter, Depends, HTTPException, Query

from app.clients.openalex import OpenAlexClient, OpenAlexUpstreamError, get_openalex_client
from app.core.config import settings
from app.models.schemas import InstitutionItem, InstitutionSearchResponse

router = APIRouter(tags=["institutions"])


@router.get("/institutions", response_model=InstitutionSearchResponse)
async def search_institutions(
    query: str = Query(..., min_length=2, description="Institution query"),
    limit: int = Query(10, ge=1, le=settings.max_page_size),
    client: OpenAlexClient = Depends(get_openalex_client),
) -> InstitutionSearchResponse:
    try:
        payload = await client.search_institutions(query=query.strip(), limit=limit)
    except OpenAlexUpstreamError as exc:
        raise HTTPException(status_code=502, detail="OpenAlex unavailable") from exc

    results = [
        InstitutionItem(
            institution_id=item.get("id", ""),
            name=item.get("display_name", ""),
            country_code=item.get("country_code"),
            works_count=item.get("works_count") or 0,
            cited_by_count=item.get("cited_by_count") or 0,
        )
        for item in payload.get("results", [])
    ]

    total = payload.get("meta", {}).get("count", len(results))
    return InstitutionSearchResponse(
        query=query,
        limit=limit,
        total=total,
        results=results,
    )
