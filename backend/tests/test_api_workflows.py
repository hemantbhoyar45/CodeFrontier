from uuid import uuid4


def _register(client, *, email: str, organization_name: str):
    response = client.post(
        "/api/v1/auth/register",
        json={
            "full_name": "Test User",
            "email": email,
            "password": "a-secure-test-password",
            "organization_name": organization_name,
        },
    )
    assert response.status_code == 201
    return response.json()["data"]


def test_auth_project_document_knowledge_and_handover_workflow(api_client) -> None:
    identity = _register(
        api_client, email=f"{uuid4()}@example.com", organization_name="Example Org"
    )
    organization_id = identity["organization"]["id"]
    headers = {"Authorization": f"Bearer {identity['access_token']}"}

    me = api_client.get("/api/v1/auth/me", headers=headers)
    assert me.status_code == 200
    assert me.json()["data"]["email"].endswith("@example.com")

    project_response = api_client.post(
        f"/api/v1/organizations/{organization_id}/projects",
        headers=headers,
        json={"name": "Continuity", "description": "Core project"},
    )
    assert project_response.status_code == 201
    project_id = project_response.json()["data"]["id"]

    document = api_client.post(
        f"/api/v1/organizations/{organization_id}/projects/{project_id}/documents",
        headers=headers,
        json={"title": "Design notes", "content_type": "text/plain"},
    )
    assert document.status_code == 201
    assert document.json()["data"]["status"] == "queued"

    knowledge = api_client.post(
        f"/api/v1/organizations/{organization_id}/projects/{project_id}/knowledge",
        headers=headers,
        json={"title": "Decision", "content": "Keep the modular monolith.", "kind": "decision"},
    )
    assert knowledge.status_code == 201

    handover = api_client.post(
        f"/api/v1/organizations/{organization_id}/projects/{project_id}/handovers",
        headers=headers,
        json={"title": "Team transition", "content": {"next_steps": ["Review open work"]}},
    )
    assert handover.status_code == 201
    assert handover.json()["data"]["content"]["next_steps"] == ["Review open work"]


def test_organization_membership_prevents_cross_tenant_project_access(api_client) -> None:
    owner = _register(
        api_client, email=f"{uuid4()}@example.com", organization_name="Tenant One"
    )
    other_user = _register(
        api_client, email=f"{uuid4()}@example.com", organization_name="Tenant Two"
    )
    owner_headers = {"Authorization": f"Bearer {owner['access_token']}"}
    other_headers = {"Authorization": f"Bearer {other_user['access_token']}"}
    tenant_id = owner["organization"]["id"]
    other_tenant_id = other_user["organization"]["id"]

    project = api_client.post(
        f"/api/v1/organizations/{tenant_id}/projects",
        headers=owner_headers,
        json={"name": "Private"},
    )
    assert project.status_code == 201
    project_id = project.json()["data"]["id"]

    response = api_client.get(
        f"/api/v1/organizations/{tenant_id}/projects/{project_id}",
        headers=other_headers,
    )
    assert response.status_code == 404

    cross_tenant_reference = api_client.get(
        f"/api/v1/organizations/{other_tenant_id}/projects/{project_id}",
        headers=other_headers,
    )
    assert cross_tenant_reference.status_code == 404


def test_api_returns_consistent_validation_error_envelope(api_client) -> None:
    response = api_client.post(
        "/api/v1/auth/register",
        json={
            "full_name": "Test User",
            "email": "not-an-email",
            "password": "short",
            "organization_name": "Example Org",
        },
    )
    assert response.status_code == 422
    assert response.json()["error"]["code"] == "validation_error"
