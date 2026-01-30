"""Authentication tests for multi-key system."""


def test_missing_api_key(client, mock_audit_service):
    """Request without API key should return 401."""
    response = client.get("/api/v1/data/landings?country=zanzibar")
    assert response.status_code == 401
    assert "Missing API key" in response.json()["detail"]

    # Verify audit log was created for auth failure
    mock_audit_service.log_auth_failure.assert_called_once()


def test_invalid_api_key(client, mock_audit_service):
    """Request with invalid API key should return 403."""
    response = client.get(
        "/api/v1/data/landings?country=zanzibar",
        headers={"X-API-Key": "wrong-key"},
    )
    assert response.status_code == 403
    assert "Invalid API key" in response.json()["detail"]

    # Verify audit log was created for auth failure
    mock_audit_service.log_auth_failure.assert_called_once()


def test_disabled_api_key(client, mock_audit_service):
    """Request with disabled API key should return 403."""
    response = client.get(
        "/api/v1/data/landings?country=zanzibar",
        headers={"X-API-Key": "test-disabled-key"},
    )
    assert response.status_code == 403
    assert "disabled" in response.json()["detail"].lower()

    # Verify audit log was created for auth failure
    mock_audit_service.log_auth_failure.assert_called_once()


def test_valid_admin_key(client, auth_headers, mock_audit_service):
    """Request with valid admin API key should succeed."""
    response = client.get(
        "/api/v1/data/landings?country=zanzibar",
        headers=auth_headers,
    )
    # Should not be 401 or 403
    assert response.status_code not in [401, 403]

    # Verify audit logs were created
    mock_audit_service.log_auth_success.assert_called_once()
    # Permission check and data access should also be logged
    assert mock_audit_service.log_permission_check.called
    assert mock_audit_service.log_data_access.called


def test_restricted_key_allowed_country(client, restricted_auth_headers, mock_audit_service):
    """Restricted key should access allowed country (zanzibar)."""
    response = client.get(
        "/api/v1/data/landings?country=zanzibar",
        headers=restricted_auth_headers,
    )
    # Should succeed
    assert response.status_code not in [401, 403]

    # Verify audit logs
    mock_audit_service.log_auth_success.assert_called_once()
    assert mock_audit_service.log_permission_check.called


def test_restricted_key_denied_country(client, restricted_auth_headers, mock_audit_service):
    """Restricted key should be denied for non-allowed country (tls)."""
    response = client.get(
        "/api/v1/data/landings?country=tls",
        headers=restricted_auth_headers,
    )
    # Should be denied
    assert response.status_code == 403
    assert "country" in response.json()["detail"].lower()

    # Verify permission denial was logged
    assert mock_audit_service.log_permission_check.called
