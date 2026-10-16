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


def test_several_api_keys(client, monkeypatch):
    """Any key in the comma-separated list is accepted, nothing else."""
    from peskas_api.core import auth

    monkeypatch.setattr(auth.settings, "api_secret_key", "key-one, key-two,")
    url = "/api/v1/data/landings?country=TLS&year=2023"
    for key in ("key-one", "key-two"):
        assert client.get(url, headers={"X-API-Key": key}).status_code not in [401, 403]
    for key in ("key-one, key-two,", "key", " "):
        assert client.get(url, headers={"X-API-Key": key}).status_code == 403


def test_metadata_needs_no_api_key(client):
    """Field descriptions are documentation: open datasets republish them."""
    for path in ("/metadata", "/metadata/landings", "/metadata/landings/fields/trip_id"):
        response = client.get(f"/api/v1{path}")
        assert response.status_code == 200, path
    fields = client.get("/api/v1/metadata/landings").json()["fields"]
    assert "trip_id" in fields
