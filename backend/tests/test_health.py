def test_health(client):
    response = client.get("/api/v1/health")

    assert response.status_code == 200
    payload = response.json()
    assert payload["status"] == "ok"
    assert payload["service"] == "research-cold-emailer-backend"
    assert payload["version"] == "v1"
