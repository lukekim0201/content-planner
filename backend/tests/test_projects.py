from tests.conftest import auth_headers


def test_create_and_list_projects(client):
    headers = auth_headers(client, "usera@example.com")
    create_response = client.post("/projects", json={"title": "Osaka Vlog"}, headers=headers)
    assert create_response.status_code == 201
    assert create_response.json()["status"] == "IDEA"

    list_response = client.get("/projects", headers=headers)
    assert list_response.status_code == 200
    titles = [p["title"] for p in list_response.json()]
    assert "Osaka Vlog" in titles


def test_create_project_rejects_blank_title(client):
    headers = auth_headers(client, "blank@example.com")
    response = client.post("/projects", json={"title": "   "}, headers=headers)
    assert response.status_code == 422


def test_kanban_status_transition(client):
    headers = auth_headers(client, "kanban@example.com")
    project = client.post("/projects", json={"title": "Ad #3"}, headers=headers).json()

    response = client.patch(
        f"/projects/{project['id']}", json={"status": "PRODUCTION"}, headers=headers
    )
    assert response.status_code == 200
    assert response.json()["status"] == "PRODUCTION"


def test_project_full_includes_script_and_assets(client):
    headers = auth_headers(client, "full@example.com")
    project = client.post("/projects", json={"title": "Full view"}, headers=headers).json()

    response = client.get(f"/projects/{project['id']}/full", headers=headers)
    assert response.status_code == 200
    body = response.json()
    assert body["script"] is None
    assert body["assets"] == []


def test_delete_project_cascades(client):
    headers = auth_headers(client, "cascade@example.com")
    project = client.post("/projects", json={"title": "To delete"}, headers=headers).json()
    client.post(f"/projects/{project['id']}/script", json={"content": "<p>hi</p>"}, headers=headers)

    delete_response = client.delete(f"/projects/{project['id']}", headers=headers)
    assert delete_response.status_code == 204

    get_response = client.get(f"/projects/{project['id']}", headers=headers)
    assert get_response.status_code == 404


def test_user_cannot_access_another_users_project(client):
    token_a = auth_headers(client, "usera2@example.com")
    project = client.post(
        "/projects", json={"title": "User A's Secret Project"}, headers=token_a
    ).json()

    token_b = auth_headers(client, "userb2@example.com")
    get_response = client.get(f"/projects/{project['id']}", headers=token_b)
    assert get_response.status_code == 404  # 404, not 403 — don't leak existence


def test_user_cannot_delete_another_users_project(client):
    token_a = auth_headers(client, "usera3@example.com")
    project = client.post(
        "/projects", json={"title": "Another Secret Project"}, headers=token_a
    ).json()

    token_b = auth_headers(client, "userb3@example.com")
    delete_response = client.delete(f"/projects/{project['id']}", headers=token_b)
    assert delete_response.status_code == 404

    get_response = client.get(f"/projects/{project['id']}", headers=token_a)
    assert get_response.status_code == 200
