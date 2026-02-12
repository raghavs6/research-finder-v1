from pydantic import BaseModel, Field


class HealthResponse(BaseModel):
    status: str
    service: str
    version: str


class InstitutionItem(BaseModel):
    institution_id: str
    name: str
    country_code: str | None = None
    works_count: int = 0
    cited_by_count: int = 0


class InstitutionSearchResponse(BaseModel):
    query: str
    limit: int
    total: int
    results: list[InstitutionItem]


class WorkItem(BaseModel):
    work_id: str
    title: str
    publication_year: int | None = None
    venue: str | None = None
    openalex_url: str | None = None


class DiscoveryAuthorResult(BaseModel):
    author_id: str
    author_name: str
    institution_name: str | None = None
    score: float
    matching_works_count: int
    recent_works_count: int
    top_venue_works_count: int
    top_works: list[WorkItem]


class DiscoveryResponse(BaseModel):
    query: str
    institution_id: str
    offset: int
    limit: int
    total: int
    results: list[DiscoveryAuthorResult]


class ErrorResponse(BaseModel):
    detail: str = Field(..., examples=["Upstream service unavailable"])
