from app.clients.openalex import OpenAlexUpstreamError, get_openalex_client
from app.main import app


MOCK_WORKS = {
    "results": [
        {
            "id": "https://openalex.org/W1",
            "display_name": "Machine Learning for Healthcare",
            "publication_year": 2025,
            "primary_location": {"source": {"display_name": "neurips"}},
            "abstract_inverted_index": {
                "machine": [0],
                "learning": [1],
                "healthcare": [2],
            },
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
            "primary_location": {"source": {"display_name": "icml"}},
            "abstract_inverted_index": {
                "deep": [0],
                "learning": [1],
                "systems": [2],
                "machine": [3],
            },
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
            "primary_location": {"source": {"display_name": "siggraph"}},
            "abstract_inverted_index": {"graphics": [0]},
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
    async def search_works_by_topic_and_institution(self, topic: str, institution_id: str) -> dict:
        return MOCK_WORKS


class FailingDiscoveryClient:
    async def search_works_by_topic_and_institution(self, topic: str, institution_id: str) -> dict:
        raise OpenAlexUpstreamError("down")


class NullPrimaryLocationDiscoveryClient:
    async def search_works_by_topic_and_institution(self, topic: str, institution_id: str) -> dict:
        return {
            "results": [
                {
                    "id": "https://openalex.org/W9",
                    "display_name": "Machine Learning Survey",
                    "publication_year": 2024,
                    "primary_location": None,
                    "abstract_inverted_index": {"machine": [0], "learning": [1]},
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
        params={"topic": "machine learning", "institution_id": "https://openalex.org/I1", "offset": 0, "limit": 10},
    )

    assert response.status_code == 200
    payload = response.json()
    assert payload["query"] == "machine learning"
    assert payload["institution_id"] == "https://openalex.org/I1"
    assert payload["total"] == 2
    assert len(payload["results"]) == 2
    assert payload["results"][0]["author_name"] == "Alice Zhang"
    assert payload["results"][0]["score"] >= payload["results"][1]["score"]


def test_discovery_pagination(client):
    app.dependency_overrides[get_openalex_client] = lambda: FakeDiscoveryClient()

    response = client.get(
        "/api/v1/discovery",
        params={"topic": "machine learning", "institution_id": "https://openalex.org/I1", "offset": 1, "limit": 1},
    )

    assert response.status_code == 200
    payload = response.json()
    assert payload["total"] == 2
    assert len(payload["results"]) == 1


def test_discovery_upstream_error_maps_to_502(client):
    app.dependency_overrides[get_openalex_client] = lambda: FailingDiscoveryClient()

    response = client.get(
        "/api/v1/discovery",
        params={"topic": "machine learning", "institution_id": "https://openalex.org/I1"},
    )

    assert response.status_code == 502
    assert response.json()["detail"] == "OpenAlex unavailable"


def test_discovery_handles_null_primary_location_without_500(client):
    app.dependency_overrides[get_openalex_client] = lambda: NullPrimaryLocationDiscoveryClient()

    response = client.get(
        "/api/v1/discovery",
        params={"topic": "machine learning", "institution_id": "https://openalex.org/I1"},
    )

    assert response.status_code == 200
    payload = response.json()
    assert payload["total"] == 1
    assert payload["results"][0]["author_name"] == "Dana Lee"
    assert payload["results"][0]["top_works"][0]["venue"] is None
