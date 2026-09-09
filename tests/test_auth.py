def test_register_success(client):
    response = client.post(
        "/auth/register", json={"email": "new@test.com", "password": "password123"}
    )
    assert response.status_code == 200
    assert response.json()["email"] == "new@test.com"


def test_register_duplicate_email(client):
    client.post("/auth/register", json={"email": "dup@test.com", "password": "password123"})
    response = client.post(
        "/auth/register", json={"email": "dup@test.com", "password": "another_pass1"}
    )
    assert response.status_code == 400


def test_login_success(client):
    client.post("/auth/register", json={"email": "login@test.com", "password": "password123"})
    response = client.post(
        "/auth/login", json={"email": "login@test.com", "password": "password123"}
    )
    assert response.status_code == 200
    assert "access_token" in response.json()


def test_login_wrong_password(client):
    client.post("/auth/register", json={"email": "wrong@test.com", "password": "correctpass"})
    response = client.post(
        "/auth/login", json={"email": "wrong@test.com", "password": "wrongpass"}
    )
    assert response.status_code == 401