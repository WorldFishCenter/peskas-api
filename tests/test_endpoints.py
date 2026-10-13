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
    assert [r["catch_taxon"] for r in data["data"]] == ["MZZ"]


def test_get_landings_with_multiple_catch_taxa(client, auth_headers):
    """Should return rows matching any of the comma-separated species codes."""
    response = client.get(
        "/api/v1/data/landings?country=zanzibar&catch_taxon=MZZ,SKJ&format=json",
        headers=auth_headers,
    )
    assert response.status_code == 200
    taxa = {r["catch_taxon"] for r in response.json()["data"]}
    assert taxa == {"MZZ", "SKJ"}


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


def test_invalid_date_range(client, auth_headers):
    """date_to before date_from should return 422."""
    response = client.get(
        "/api/v1/data/landings?country=zanzibar&date_from=2025-02-01&date_to=2025-01-01",
        headers=auth_headers,
    )
    assert response.status_code == 422


def test_openapi_param_descriptions(client):
    """Query parameters should expose their descriptions in the OpenAPI schema."""
    schema = client.get("/openapi.json").json()
    params = schema["paths"]["/api/v1/data/landings"]["get"]["parameters"]
    assert all(p.get("description") for p in params)


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


def test_favicon(client):
    """Browsers asking for /favicon.ico should get the Peskas icon."""
    response = client.get("/favicon.ico")
    assert response.status_code == 200
    assert response.headers["content-type"] in ["image/x-icon", "image/vnd.microsoft.icon"]
    assert response.content[:4] == b"\x00\x00\x01\x00"  # ICO file signature


def test_static_brand_files(client):
    """The Peskas favicons and logo should be served from /static."""
    for path, content_type in [
        ("/static/favicon.svg", "image/svg+xml"),
        ("/static/apple-touch-icon.png", "image/png"),
        ("/static/peskas-logo.svg", "image/svg+xml"),
    ]:
        response = client.get(path)
        assert response.status_code == 200
        assert response.headers["content-type"].startswith(content_type)


def test_docs_pages_link_favicons(client):
    """Swagger UI and ReDoc should keep their URLs and link the Peskas favicons."""
    for path, title in [("/docs", "Swagger UI"), ("/redoc", "ReDoc")]:
        response = client.get(path)
        assert response.status_code == 200
        assert f"<title>Peskas Fishery Data API - {title}</title>" in response.text
        assert '<link rel="icon" href="/favicon.ico" sizes="32x32">' in response.text
        assert '<link rel="icon" href="/static/favicon.svg" type="image/svg+xml">' in response.text
        assert '<link rel="apple-touch-icon" href="/static/apple-touch-icon.png">' in response.text
        assert "fastapi.tiangolo.com/img/favicon.png" not in response.text
    assert client.get("/docs/oauth2-redirect").status_code == 200
    # ReDoc gets the brand kit's logo size and clear space through its theme option
    assert """<redoc theme='{"logo": {"gutter": "20px",""" in client.get("/redoc").text


def test_openapi_x_logo(client):
    """The OpenAPI schema should carry the Peskas logo for ReDoc, and no docs routes."""
    schema = client.get("/openapi.json").json()
    assert schema["info"]["x-logo"] == {
        "url": "/static/peskas-logo.svg",
        "altText": "Peskas",
        "href": "https://peskas.org",
    }
    assert all(path.startswith("/api/v1/") for path in schema["paths"])


def test_get_district_months_csv(client, auth_headers):
    """Should return one CSV row per district and month."""
    response = client.get(
        "/api/v1/data/district-months?country=zanzibar",
        headers=auth_headers,
    )
    assert response.status_code == 200
    assert "text/csv" in response.headers["content-type"]
    assert "district-months_zanzibar.csv" in response.headers["content-disposition"]
    header = response.text.splitlines()[0].split(",")
    assert header[:2] == ["country", "month"]
    assert len(response.text.splitlines()) == 4


def test_get_district_months_filters_district_and_month(client, auth_headers):
    """gaul_2 and the month range should narrow the rows."""
    response = client.get(
        "/api/v1/data/district-months?country=zanzibar&gaul_2=106434"
        "&date_from=2026-03-01&date_to=2026-03-31&format=json",
        headers=auth_headers,
    )
    assert response.status_code == 200
    rows = response.json()["data"]
    assert [(r["gaul_2_name"], r["n_submissions"]) for r in rows] == [("Kati", 74)]
    assert rows[0]["month"].startswith("2026-03-01")


def test_get_district_months_empty_figures_are_null(client, auth_headers):
    """A month with nothing recorded keeps its row, with empty figures."""
    response = client.get(
        "/api/v1/data/district-months?country=zanzibar&date_to=2026-02-28&format=json",
        headers=auth_headers,
    )
    row = response.json()["data"][0]
    assert row["n_submissions"] == 0
    assert row["mean_catch_kg"] is None


def test_get_district_months_requires_auth(client):
    """Data endpoints need the API key."""
    response = client.get("/api/v1/data/district-months?country=zanzibar")
    assert response.status_code == 401


def test_district_months_metadata(client):
    """The field descriptions are served without a key, in file order."""
    response = client.get("/api/v1/metadata/district-months")
    assert response.status_code == 200
    fields = response.json()["fields"]
    assert len(fields) == 23
    assert fields["relative_error_catch_fao"]["unit"] == "share"

    listed = client.get("/api/v1/metadata").json()["dataset_types"]
    assert listed == ["landings", "district-months"]
