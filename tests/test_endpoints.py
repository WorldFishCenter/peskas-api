"""Endpoint integration tests."""


def test_health_check(client):
    """Health endpoint should work without auth."""
    response = client.get("/api/v1/health")
    assert response.status_code == 200
    data = response.json()
    # In test mode, GCS may not be accessible, so status could be "degraded"
    assert data["status"] in ["healthy", "degraded"]
    assert "version" in data
    assert "gcs_accessible" in data
    assert isinstance(data["gcs_accessible"], bool)


def test_get_landings_csv(client, auth_headers):
    """Should return CSV data."""
    response = client.get(
        "/api/v1/data/landings?country=zanzibar",
        headers=auth_headers,
    )
    assert response.status_code == 200
    assert "text/csv" in response.headers["content-type"]
    # Check CSV has content
    assert len(response.text) > 0
    # Check it contains actual column headers
    assert "trip_id" in response.text or "landing_date" in response.text


def test_get_landings_json(client, auth_headers):
    """Should return JSON data when requested."""
    response = client.get(
        "/api/v1/data/landings?country=zanzibar&format=json",
        headers=auth_headers,
    )
    assert response.status_code == 200
    assert response.headers["content-type"] == "application/json"
    data = response.json()
    assert "data" in data
    assert isinstance(data["data"], list)


def test_get_landings_with_date_filter(client, auth_headers):
    """Should filter by date range."""
    response = client.get(
        "/api/v1/data/landings?country=zanzibar&date_from=2025-02-01&date_to=2025-02-28&format=json",
        headers=auth_headers,
    )
    assert response.status_code == 200
    data = response.json()
    assert "data" in data


def test_get_landings_with_gaul_1_filter(client, auth_headers):
    """Should filter by GAUL level 1 code."""
    response = client.get(
        "/api/v1/data/landings?country=zanzibar&gaul_1=1696&format=json",
        headers=auth_headers,
    )
    assert response.status_code == 200
    data = response.json()
    assert "data" in data


def test_get_landings_with_catch_taxon_filter(client, auth_headers):
    """Should filter by FAO ASFIS species code."""
    response = client.get(
        "/api/v1/data/landings?country=zanzibar&catch_taxon=MZZ&format=json",
        headers=auth_headers,
    )
    assert response.status_code == 200
    data = response.json()
    assert "data" in data


def test_get_landings_with_combined_filters(client, auth_headers):
    """Should handle multiple filters."""
    response = client.get(
        "/api/v1/data/landings?country=zanzibar&gaul_1=1696&catch_taxon=SKJ&date_from=2025-01-01&format=json",
        headers=auth_headers,
    )
    assert response.status_code == 200
    data = response.json()
    assert "data" in data


def test_missing_required_params(client, auth_headers):
    """Missing required params should return 422."""
    response = client.get(
        "/api/v1/data/landings",
        headers=auth_headers,
    )
    assert response.status_code == 422


def test_csv_content_disposition(client, auth_headers):
    """CSV response should have Content-Disposition header."""
    response = client.get(
        "/api/v1/data/landings?country=zanzibar",
        headers=auth_headers,
    )
    assert response.status_code == 200
    assert "Content-Disposition" in response.headers
    assert "attachment" in response.headers["Content-Disposition"]
    assert "landings_zanzibar_validated.csv" in response.headers["Content-Disposition"]
