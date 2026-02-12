from app.clients.openalex import OpenAlexUpstreamError, get_openalex_client
from app.main import app


class FakeInstitutionsClient:
    async def search_institutions(self, query: str, limit: int) -> dict:
        return {
            "meta": {"count": 2},
            "results": [
                {
                    "id": "https://openalex.org/I1",
                    "display_name": "MIT",
                    "country_code": "US",
                    "works_count": 100,
                    "cited_by_count": 1000,
                },
                {
                    "id": "https://openalex.org/I2",
                    "display_name": "Stanford University",
                    "country_code": "US",
                    "works_count": 90,
                    "cited_by_count": 950,
                },
            ],
        }


class FailingInstitutionsClient:
    async def search_institutions(self, query: str, limit: int) -> dict:
        raise OpenAlexUpstreamError("down")


def test_search_institutions_happy_path(client):
    app.dependency_overrides[get_openalex_client] = lambda: FakeInstitutionsClient()

    response = client.get("/api/v1/institutions", params={"query": "stanford", "limit": 2})

    assert response.status_code == 200
    payload = response.json()
    assert payload["query"] == "stanford"
    assert payload["limit"] == 2
    assert payload["total"] == 2
    assert len(payload["results"]) == 2
    assert payload["results"][0]["name"] == "MIT"


def test_search_institutions_validation_error(client):
    response = client.get("/api/v1/institutions", params={"query": "a"})

    assert response.status_code == 422


def test_search_institutions_upstream_error_maps_to_502(client):
    app.dependency_overrides[get_openalex_client] = lambda: FailingInstitutionsClient()

    response = client.get("/api/v1/institutions", params={"query": "stanford", "limit": 2})

    assert response.status_code == 502
    assert response.json()["detail"] == "OpenAlex unavailable"
