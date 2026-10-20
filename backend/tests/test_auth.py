def test_signup_and_login(client):
    signup_response = client.post(
        "/signup", json={"email": "alice@example.com", "password": "testpassword123"}
    )
    assert signup_response.status_code == 200
    assert "hashed_password" not in signup_response.json()  # schema separation working

    login_response = client.post(
        "/login", json={"email": "alice@example.com", "password": "testpassword123"}
    )
    assert login_response.status_code == 200
    assert "access_token" in login_response.json()


def test_signup_normalizes_email_case(client):
    client.post("/signup", json={"email": "Mixed@Example.com", "password": "testpass123"})
    response = client.post("/login", json={"email": "mixed@example.com", "password": "testpass123"})
    assert response.status_code == 200


def test_signup_rejects_short_password(client):
    response = client.post("/signup", json={"email": "short@example.com", "password": "abc"})
    assert response.status_code == 422


def test_login_wrong_password_fails(client):
    client.post("/signup", json={"email": "bob@example.com", "password": "correctpass"})
    response = client.post("/login", json={"email": "bob@example.com", "password": "wrongpass"})
    assert response.status_code == 401


def test_duplicate_signup_rejected(client):
    client.post("/signup", json={"email": "carol@example.com", "password": "pass1234"})
    response = client.post("/signup", json={"email": "carol@example.com", "password": "pass4567"})
    assert response.status_code == 400


def test_me_requires_token(client):
    response = client.get("/auth/me")
    assert response.status_code in (401, 403)


def test_me_returns_current_user(client):
    from tests.conftest import auth_headers

    headers = auth_headers(client, "dana@example.com")
    response = client.get("/auth/me", headers=headers)
    assert response.status_code == 200
    assert response.json()["email"] == "dana@example.com"
