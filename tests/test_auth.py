"""Authentication tests."""


def test_missing_api_key(client):
    """Request without API key should return 401."""
    response = client.get("/api/v1/data/landings?country=TLS&year=2023")
    assert response.status_code == 401
    assert "Missing API key" in response.json()["detail"]


def test_invalid_api_key(client):
    """Request with invalid API key should return 403."""
    response = client.get(
        "/api/v1/data/landings?country=TLS&year=2023",
        headers={"X-API-Key": "wrong-key"},
    )
    assert response.status_code == 403
    assert "Invalid API key" in response.json()["detail"]


def test_valid_api_key(client, auth_headers):
    """Request with valid API key should succeed."""
    response = client.get(
        "/api/v1/data/landings?country=TLS&year=2023",
        headers=auth_headers,
    )
    # Should not be 401 or 403
    assert response.status_code not in [401, 403]
