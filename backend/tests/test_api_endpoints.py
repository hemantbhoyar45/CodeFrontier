from uuid import uuid4


def _register(client, *, email: str, organization_name: str) -> dict[str, object]:
    response = client.post(
        "/api/v1/auth/register",
        json={
            "full_name": "API Test",
            "email": email,
            "password": "a-secure-test-password",
            "organization_name": organization_name,
        },
    )
    assert response.status_code == 201
    return response.json()["data"]


def test_organization_user_project_membership_and_content_apis(api_client) -> None:
    user = _register(api_client, email=f"{uuid4()}@example.com", organization_name="Primary")
    other_user = _register(api_client, email=f"{uuid4()}@example.com", organization_name="Other")
    token = user["access_token"]
    headers = {"Authorization": f"Bearer {token}"}
    organization_id = user["organization"]["id"]

    login = api_client.post(
        "/api/v1/auth/login",
        json={"email": user["user"]["email"], "password": "a-secure-test-password"},
    )
    assert login.status_code == 200
    assert login.json()["data"]["token_type"] == "bearer"

    bad_login = api_client.post(
        "/api/v1/auth/login",
        json={"email": user["user"]["email"], "password": "incorrect"},
    )
    assert bad_login.status_code == 401

    organization = api_client.post(
        "/api/v1/organizations", headers=headers, json={"name": "Second Org"}
    )
    assert organization.status_code == 201
    assert api_client.get(
        f"/api/v1/organizations/{organization_id}", headers=headers
    ).status_code == 200
    organizations = api_client.get(
        "/api/v1/organizations?limit=1&sort_by=name",
        headers=headers,
    )
    assert organizations.status_code == 200
    assert organizations.json()["meta"] == {"count": 2, "limit": 1, "offset": 0}

    member = api_client.post(
        f"/api/v1/organizations/{organization_id}/members",
        headers=headers,
        json={"email": other_user["user"]["email"], "role": "member"},
    )
    assert member.status_code == 201
    members = api_client.get(
        f"/api/v1/organizations/{organization_id}/members?limit=10",
        headers=headers,
    )
    assert members.status_code == 200
    assert members.json()["meta"]["count"] == 2
    users = api_client.get(
        f"/api/v1/organizations/{organization_id}/users?search=API&sort_by=full_name",
        headers=headers,
    )
    assert users.status_code == 200
    assert users.json()["meta"]["count"] == 2

    base = f"/api/v1/organizations/{organization_id}"
    project_response = api_client.post(
        f"{base}/projects", headers=headers, json={"name": "API project"}
    )
    assert project_response.status_code == 201
    project_id = project_response.json()["data"]["id"]
    project_path = f"{base}/projects/{project_id}"
    assert api_client.get(f"{base}/projects?status=active&sort_by=name", headers=headers).json()[
        "meta"
    ]["count"] == 1
    assert api_client.get(project_path, headers=headers).status_code == 200
    update = api_client.patch(
        project_path, headers=headers, json={"name": "Updated API project", "status": "paused"}
    )
    assert update.status_code == 200
    assert update.json()["data"]["status"] == "paused"

    project_members = api_client.get(f"{project_path}/members", headers=headers)
    assert project_members.status_code == 200
    assert project_members.json()["meta"]["count"] == 1
    added_project_member = api_client.post(
        f"{project_path}/members",
        headers=headers,
        json={"user_id": other_user["user"]["id"], "role": "viewer"},
    )
    assert added_project_member.status_code == 201
    viewer_write = api_client.post(
        f"{project_path}/knowledge",
        headers={"Authorization": f"Bearer {other_user['access_token']}"},
        json={"title": "Denied", "content": "Viewer cannot add items"},
    )
    assert viewer_write.status_code == 403
    assert api_client.delete(
        f"{project_path}/members/{other_user['user']['id']}", headers=headers
    ).status_code == 204

    documents_path = f"{project_path}/documents"
    document = api_client.post(
        documents_path,
        headers=headers,
        json={"title": "Metadata", "source_uri": "https://example.test/doc"},
    )
    assert document.status_code == 201
    document_id = document.json()["data"]["id"]
    assert api_client.get(
        f"{documents_path}?status=queued&sort_by=title", headers=headers
    ).json()["meta"]["count"] == 1
    document_path = f"{documents_path}/{document_id}"
    assert api_client.get(document_path, headers=headers).status_code == 200
    assert api_client.patch(
        document_path, headers=headers, json={"status": "ready"}
    ).status_code == 200
    assert api_client.delete(document_path, headers=headers).status_code == 204
    assert api_client.get(document_path, headers=headers).status_code == 404

    knowledge_path = f"{project_path}/knowledge"
    knowledge = api_client.post(
        knowledge_path,
        headers=headers,
        json={"title": "Finding", "content": "Validated", "kind": "fact"},
    )
    assert knowledge.status_code == 201
    item_id = knowledge.json()["data"]["id"]
    item_path = f"{knowledge_path}/{item_id}"
    assert api_client.get(item_path, headers=headers).status_code == 200
    assert api_client.get(
        f"{knowledge_path}?kind=fact&sort_by=title", headers=headers
    ).json()["meta"]["count"] == 1
    assert api_client.patch(
        item_path, headers=headers, json={"status": "verified"}
    ).status_code == 200
    assert api_client.delete(item_path, headers=headers).status_code == 204

    handovers_path = f"{project_path}/handovers"
    handover = api_client.post(
        handovers_path,
        headers=headers,
        json={"title": "Handover", "recipient_role": "on-call", "content": {"todo": []}},
    )
    assert handover.status_code == 201
    report_id = handover.json()["data"]["id"]
    assert api_client.get(
        f"{handovers_path}?sort_by=title", headers=headers
    ).json()["meta"]["count"] == 1
    assert api_client.get(f"{handovers_path}/{report_id}", headers=headers).status_code == 200

    audit = api_client.get(f"{base}/audit-logs?limit=100", headers=headers)
    assert audit.status_code == 200
    assert audit.json()["meta"]["count"] > 0

    assert api_client.delete(project_path, headers=headers).status_code == 204
    assert api_client.get(project_path, headers=headers).status_code == 404


def test_registration_rejects_duplicate_email_and_protected_routes_require_auth(api_client) -> None:
    email = f"{uuid4()}@example.com"
    _register(api_client, email=email, organization_name="Once")
    duplicate = api_client.post(
        "/api/v1/auth/register",
        json={
            "full_name": "Duplicate",
            "email": email,
            "password": "another-secure-password",
            "organization_name": "Duplicate Org",
        },
    )
    assert duplicate.status_code == 409
    assert duplicate.json()["error"]["message"] == "An account with this email already exists"
    assert api_client.get("/api/v1/organizations").status_code == 401
