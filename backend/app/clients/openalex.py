import asyncio
from collections.abc import Mapping

import httpx

from app.core.config import settings


class OpenAlexUpstreamError(Exception):
    pass


class OpenAlexClient:
    def __init__(self) -> None:
        self.base_url = settings.openalex_base_url
        self.timeout = settings.openalex_timeout_seconds
        self.max_retries = settings.openalex_max_retries
        self.retry_backoff = settings.openalex_retry_backoff_seconds

    async def _request(self, path: str, params: Mapping[str, str | int]) -> dict:
        url = f"{self.base_url}{path}"
        attempts = self.max_retries + 1
        last_error: Exception | None = None

        for attempt in range(attempts):
            try:
                async with httpx.AsyncClient(timeout=self.timeout) as client:
                    response = await client.get(url, params=params)
                response.raise_for_status()
                return response.json()
            except (httpx.TimeoutException, httpx.NetworkError) as exc:
                last_error = exc
            except httpx.HTTPStatusError as exc:
                status_code = exc.response.status_code
                last_error = exc
                if status_code < 500:
                    raise OpenAlexUpstreamError("OpenAlex returned a non-retryable error") from exc

            if attempt < attempts - 1:
                await asyncio.sleep(self.retry_backoff * (2**attempt))

        raise OpenAlexUpstreamError("OpenAlex unavailable after retries") from last_error

    async def search_institutions(self, query: str, limit: int) -> dict:
        safe_limit = min(max(1, limit), settings.max_page_size)
        payload = await self._request(
            "/institutions",
            {
                "search": query,
                "per-page": safe_limit,
                "select": "id,display_name,country_code,works_count,cited_by_count",
            },
        )
        return payload

    async def search_works_by_topic_and_institution(
        self,
        topic: str,
        institution_id: str,
        per_page: int | None = None,
    ) -> dict:
        normalized_institution_id = institution_id.rsplit("/", maxsplit=1)[-1]
        safe_per_page = per_page or settings.openalex_default_per_page
        safe_per_page = min(max(1, safe_per_page), settings.openalex_max_per_page)
        payload = await self._request(
            "/works",
            {
                "search": topic,
                "filter": f"institutions.id:{normalized_institution_id}",
                "per-page": safe_per_page,
                "sort": "publication_date:desc",
                "select": "id,display_name,publication_year,primary_location,authorships,abstract_inverted_index",
            },
        )
        return payload


def get_openalex_client() -> OpenAlexClient:
    return OpenAlexClient()
