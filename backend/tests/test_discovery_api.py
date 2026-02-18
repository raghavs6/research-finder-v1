from app.clients.openalex import OpenAlexUpstreamError, get_openalex_client
from app.main import app


MOCK_WORKS = {
    "results": [
        {
            "id": "https://openalex.org/W1",
            "display_name": "Machine Learning for Healthcare",
            "publication_year": 2025,
            "primary_location": {"source": {"display_name": "NeurIPS 2025"}},
            "authorships": [
                {
                    "author": {"id": "https://openalex.org/A1", "display_name": "Alice Zhang"},
                    "institutions": [
                        {"id": "https://openalex.org/I1", "display_name": "MIT"}
                    ],
                }
            ],
        },
        {
            "id": "https://openalex.org/W2",
            "display_name": "Deep Learning Systems",
            "publication_year": 2024,
            "primary_location": {"source": {"display_name": "ICML 2024"}},
            "authorships": [
                {
                    "author": {"id": "https://openalex.org/A2", "display_name": "Bob Young"},
                    "institutions": [
                        {"id": "https://openalex.org/I1", "display_name": "MIT"}
                    ],
                },
                {
                    "author": {"id": "https://openalex.org/A1", "display_name": "Alice Zhang"},
                    "institutions": [
                        {"id": "https://openalex.org/I1", "display_name": "MIT"}
                    ],
                },
            ],
        },
        {
            "id": "https://openalex.org/W3",
            "display_name": "Computer Graphics",
            "publication_year": 2023,
            "primary_location": {"source": {"display_name": "SIGGRAPH"}},
            "authorships": [
                {
                    "author": {"id": "https://openalex.org/A3", "display_name": "Carol Smith"},
                    "institutions": [
                        {"id": "https://openalex.org/I1", "display_name": "MIT"}
                    ],
                }
            ],
        },
    ]
}


class FakeDiscoveryClient:
    async def search_works_by_institution(self, institution_id: str, per_page: int = 200) -> dict:
        return MOCK_WORKS


class FailingDiscoveryClient:
    async def search_works_by_institution(self, institution_id: str, per_page: int = 200) -> dict:
        raise OpenAlexUpstreamError("down")


class NullPrimaryLocationDiscoveryClient:
    async def search_works_by_institution(self, institution_id: str, per_page: int = 200) -> dict:
        return {
            "results": [
                {
                    "id": "https://openalex.org/W9",
                    "display_name": "Machine Learning Survey",
                    "publication_year": 2024,
                    "primary_location": None,
                    "authorships": [
                        {
                            "author": {"id": "https://openalex.org/A9", "display_name": "Dana Lee"},
                            "institutions": [{"id": institution_id, "display_name": "MIT"}],
                        }
                    ],
                }
            ]
        }


def test_discovery_happy_path(client):
    app.dependency_overrides[get_openalex_client] = lambda: FakeDiscoveryClient()

    response = client.get(
        "/api/v1/discovery",
        params={"area": "Machine Learning", "institution_id": "https://openalex.org/I1", "offset": 0, "limit": 10},
    )

    assert response.status_code == 200
    payload = response.json()
    assert payload["area"] == "Machine Learning"
    assert payload["institution_id"] == "https://openalex.org/I1"
    # Alice (2 ML venue works) and Bob (1 ML venue work); Carol is excluded (SIGGRAPH)
    assert payload["total"] == 2
    assert len(payload["results"]) == 2
    assert payload["results"][0]["author_name"] == "Alice Zhang"
    assert payload["results"][0]["score"] >= payload["results"][1]["score"]


def test_discovery_pagination(client):
    app.dependency_overrides[get_openalex_client] = lambda: FakeDiscoveryClient()

    response = client.get(
        "/api/v1/discovery",
        params={"area": "Machine Learning", "institution_id": "https://openalex.org/I1", "offset": 1, "limit": 1},
    )

    assert response.status_code == 200
    payload = response.json()
    assert payload["total"] == 2
    assert len(payload["results"]) == 1


def test_discovery_upstream_error_maps_to_502(client):
    app.dependency_overrides[get_openalex_client] = lambda: FailingDiscoveryClient()

    response = client.get(
        "/api/v1/discovery",
        params={"area": "Machine Learning", "institution_id": "https://openalex.org/I1"},
    )

    assert response.status_code == 502
    assert response.json()["detail"] == "OpenAlex unavailable"


def test_discovery_unknown_area_returns_400(client):
    app.dependency_overrides[get_openalex_client] = lambda: FakeDiscoveryClient()

    response = client.get(
        "/api/v1/discovery",
        params={"area": "Underwater Basket Weaving", "institution_id": "https://openalex.org/I1"},
    )

    assert response.status_code == 400
    assert "Unknown area" in response.json()["detail"]


def test_discovery_handles_null_primary_location_without_500(client):
    app.dependency_overrides[get_openalex_client] = lambda: NullPrimaryLocationDiscoveryClient()

    response = client.get(
        "/api/v1/discovery",
        params={"area": "Machine Learning", "institution_id": "https://openalex.org/I1"},
    )

    assert response.status_code == 200
    payload = response.json()
    # Works with null primary_location have no venue and are excluded from area-based ranking
    assert payload["total"] == 0
    assert payload["results"] == []
