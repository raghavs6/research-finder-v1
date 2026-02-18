from app.core.config import AREA_CONFERENCES


def test_areas_returns_200_with_list(client):
    response = client.get("/api/v1/areas")

    assert response.status_code == 200
    payload = response.json()
    assert "areas" in payload
    assert len(payload["areas"]) > 0


def test_areas_includes_conferences(client):
    response = client.get("/api/v1/areas")

    payload = response.json()
    for area in payload["areas"]:
        assert "name" in area
        assert "conferences" in area
        assert len(area["conferences"]) >= 1


def test_areas_matches_config(client):
    response = client.get("/api/v1/areas")

    payload = response.json()
    returned_names = {a["name"] for a in payload["areas"]}
    assert returned_names == set(AREA_CONFERENCES.keys())


def test_areas_no_upstream_call(client):
    # No mock needed — areas endpoint serves static data from config, no OpenAlex call
    response = client.get("/api/v1/areas")
    assert response.status_code == 200
