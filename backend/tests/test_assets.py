import io

from tests.conftest import auth_headers
from app import config, storage


def test_upload_asset_stores_locally_and_lists(client):
    headers = auth_headers(client, "uploader@example.com")
    project = client.post("/projects", json={"title": "P"}, headers=headers).json()

    file_content = io.BytesIO(b"fake-image-bytes")
    response = client.post(
        f"/projects/{project['id']}/assets/upload",
        headers=headers,
        files={"file": ("photo.jpg", file_content, "image/jpeg")},
    )
    assert response.status_code == 201
    body = response.json()
    assert body["asset_type"] == "IMAGE"
    assert body["file_name"] == "photo.jpg"
    assert body["size_bytes"] == len(b"fake-image-bytes")

    list_response = client.get(f"/projects/{project['id']}/assets", headers=headers)
    assert list_response.status_code == 200
    assert len(list_response.json()) == 1


def test_register_asset_with_external_url(client):
    headers = auth_headers(client, "external@example.com")
    project = client.post("/projects", json={"title": "P"}, headers=headers).json()

    response = client.post(
        f"/projects/{project['id']}/assets",
        json={
            "file_url": "https://example-bucket.s3.us-east-1.amazonaws.com/clip.mp4",
            "file_name": "clip.mp4",
            "asset_type": "VIDEO",
            "size_bytes": 1024,
        },
        headers=headers,
    )
    assert response.status_code == 201
    assert response.json()["asset_type"] == "VIDEO"


def test_delete_asset(client):
    headers = auth_headers(client, "deleter@example.com")
    project = client.post("/projects", json={"title": "P"}, headers=headers).json()
    asset = client.post(
        f"/projects/{project['id']}/assets",
        json={"file_url": "http://x/a.png", "asset_type": "IMAGE"},
        headers=headers,
    ).json()

    response = client.delete(f"/projects/{project['id']}/assets/{asset['id']}", headers=headers)
    assert response.status_code == 204

    list_response = client.get(f"/projects/{project['id']}/assets", headers=headers)
    assert list_response.json() == []


def test_delete_uploaded_asset_removes_file(client, tmp_path):
    headers = auth_headers(client, "cleanup@example.com")
    project = client.post("/projects", json={"title": "P"}, headers=headers).json()
    asset = client.post(
        f"/projects/{project['id']}/assets/upload",
        headers=headers,
        files={"file": ("photo.jpg", io.BytesIO(b"bytes"), "image/jpeg")},
    ).json()
    stored = list((tmp_path / project["id"]).iterdir())
    assert len(stored) == 1

    client.delete(f"/projects/{project['id']}/assets/{asset['id']}", headers=headers)
    assert not stored[0].exists()


def test_delete_registered_asset_cannot_escape_project_folder(client, tmp_path):
    """A client-registered file_url must never let a delete reach files
    outside that project's own upload folder."""
    victim_outside = tmp_path / "secret.txt"
    victim_outside.write_text("keep me")
    victim_other_project = tmp_path / "other-project" / "file.png"
    victim_other_project.parent.mkdir()
    victim_other_project.write_text("keep me too")

    headers = auth_headers(client, "attacker@example.com")
    project = client.post("/projects", json={"title": "P"}, headers=headers).json()
    for url in (
        f"{config.PUBLIC_BASE_URL}/uploads/{project['id']}/../secret.txt",
        f"{config.PUBLIC_BASE_URL}/uploads/other-project/file.png",
    ):
        asset = client.post(
            f"/projects/{project['id']}/assets",
            json={"file_url": url, "asset_type": "OTHER"},
            headers=headers,
        ).json()
        response = client.delete(
            f"/projects/{project['id']}/assets/{asset['id']}", headers=headers
        )
        assert response.status_code == 204

    assert victim_outside.exists()
    assert victim_other_project.exists()


def test_cannot_upload_to_another_users_project(client):
    token_a = auth_headers(client, "ownera@example.com")
    project = client.post("/projects", json={"title": "P"}, headers=token_a).json()

    token_b = auth_headers(client, "ownerb@example.com")
    file_content = io.BytesIO(b"data")
    response = client.post(
        f"/projects/{project['id']}/assets/upload",
        headers=token_b,
        files={"file": ("a.png", file_content, "image/png")},
    )
    assert response.status_code == 404


def test_get_single_asset(client):
    headers = auth_headers(client, "getter@example.com")
    project = client.post("/projects", json={"title": "P"}, headers=headers).json()
    asset = client.post(
        f"/projects/{project['id']}/assets",
        json={"file_url": "http://x/a.png", "file_name": "a.png", "asset_type": "IMAGE"},
        headers=headers,
    ).json()

    response = client.get(f"/projects/{project['id']}/assets/{asset['id']}", headers=headers)
    assert response.status_code == 200
    assert response.json()["file_name"] == "a.png"


def test_rename_asset(client):
    headers = auth_headers(client, "renamer@example.com")
    project = client.post("/projects", json={"title": "P"}, headers=headers).json()
    asset = client.post(
        f"/projects/{project['id']}/assets",
        json={"file_url": "http://x/a.png", "file_name": "old.png", "asset_type": "IMAGE"},
        headers=headers,
    ).json()

    response = client.patch(
        f"/projects/{project['id']}/assets/{asset['id']}",
        json={"file_name": "new.png"},
        headers=headers,
    )
    assert response.status_code == 200
    assert response.json()["file_name"] == "new.png"


def test_rename_asset_rejects_blank_name(client):
    headers = auth_headers(client, "renamer2@example.com")
    project = client.post("/projects", json={"title": "P"}, headers=headers).json()
    asset = client.post(
        f"/projects/{project['id']}/assets",
        json={"file_url": "http://x/a.png", "asset_type": "IMAGE"},
        headers=headers,
    ).json()

    response = client.patch(
        f"/projects/{project['id']}/assets/{asset['id']}",
        json={"file_name": "   "},
        headers=headers,
    )
    assert response.status_code == 422


def test_upload_asset_uses_s3_when_configured(client, monkeypatch):
    """With AWS creds configured, uploads should go through the S3 code
    path and produce an S3-shaped URL — verified with a fake boto3 client
    so the test suite never needs real AWS credentials."""
    monkeypatch.setattr(config, "AWS_ACCESS_KEY_ID", "fake-key")
    monkeypatch.setattr(config, "AWS_SECRET_ACCESS_KEY", "fake-secret")
    monkeypatch.setattr(config, "AWS_S3_BUCKET", "my-test-bucket")
    monkeypatch.setattr(storage, "AWS_ACCESS_KEY_ID", "fake-key")
    monkeypatch.setattr(storage, "AWS_SECRET_ACCESS_KEY", "fake-secret")
    monkeypatch.setattr(storage, "AWS_S3_BUCKET", "my-test-bucket")

    put_calls = []

    class FakeS3Client:
        def put_object(self, **kwargs):
            put_calls.append(kwargs)

    monkeypatch.setattr(storage, "_s3_client", lambda: FakeS3Client())

    headers = auth_headers(client, "s3user@example.com")
    project = client.post("/projects", json={"title": "P"}, headers=headers).json()

    file_content = io.BytesIO(b"fake-video-bytes")
    response = client.post(
        f"/projects/{project['id']}/assets/upload",
        headers=headers,
        files={"file": ("clip.mp4", file_content, "video/mp4")},
    )
    assert response.status_code == 201
    body = response.json()
    assert body["file_url"].startswith("https://my-test-bucket.s3.")
    assert len(put_calls) == 1
    assert put_calls[0]["Bucket"] == "my-test-bucket"
