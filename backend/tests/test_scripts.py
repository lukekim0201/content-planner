from tests.conftest import auth_headers
from app import config


def test_create_script_moves_project_to_scripting(client):
    headers = auth_headers(client, "writer@example.com")
    project = client.post("/projects", json={"title": "My Trip"}, headers=headers).json()
    assert project["status"] == "IDEA"

    response = client.post(
        f"/projects/{project['id']}/script", json={"content": "<p>Scene 1</p>"}, headers=headers
    )
    assert response.status_code == 201

    refreshed = client.get(f"/projects/{project['id']}", headers=headers).json()
    assert refreshed["status"] == "SCRIPTING"


def test_cannot_create_second_script(client):
    headers = auth_headers(client, "dup@example.com")
    project = client.post("/projects", json={"title": "P"}, headers=headers).json()
    client.post(f"/projects/{project['id']}/script", json={"content": "a"}, headers=headers)

    response = client.post(f"/projects/{project['id']}/script", json={"content": "b"}, headers=headers)
    assert response.status_code == 400


def test_update_script_content(client):
    headers = auth_headers(client, "editor@example.com")
    project = client.post("/projects", json={"title": "P"}, headers=headers).json()
    client.post(f"/projects/{project['id']}/script", json={"content": "v1"}, headers=headers)

    response = client.patch(
        f"/projects/{project['id']}/script", json={"content": "v2"}, headers=headers
    )
    assert response.status_code == 200
    assert response.json()["content"] == "v2"


def test_suggest_scene_without_api_key_returns_501(client, monkeypatch):
    """AI is a stretch goal — with no OPENAI_API_KEY configured, this must
    degrade gracefully, not crash, regardless of the host's real env."""
    monkeypatch.setattr(config, "OPENAI_API_KEY", None)
    headers = auth_headers(client, "ai@example.com")
    project = client.post("/projects", json={"title": "P"}, headers=headers).json()
    client.post(f"/projects/{project['id']}/script", json={"content": "<p>Intro scene</p>"}, headers=headers)

    response = client.post(f"/projects/{project['id']}/script/suggest", json={}, headers=headers)
    assert response.status_code == 501


def test_suggest_scene_requires_script(client):
    headers = auth_headers(client, "noscript@example.com")
    project = client.post("/projects", json={"title": "P"}, headers=headers).json()

    response = client.post(f"/projects/{project['id']}/script/suggest", json={}, headers=headers)
    assert response.status_code == 404
