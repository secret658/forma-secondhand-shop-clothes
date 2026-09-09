def test_account_locks_after_failed_attempts(client):
    client.post("/auth/register", json={"email": "locktest@test.com", "password": "correctpass1"})

    #5 неверных попыток подряд должны заблокировать аккаунт
    for _ in range(5):
        response = client.post(
            "/auth/login", json={"email": "locktest@test.com", "password": "wrongpass1"}
        )
        assert response.status_code == 401

    #6-я попытка, даже с ПРАВИЛЬНЫМ паролем, должна быть заблокирована
    response = client.post(
        "/auth/login", json={"email": "locktest@test.com", "password": "correctpass1"}
    )
    assert response.status_code == 423


def test_successful_login_resets_failed_counter(client):
    client.post("/auth/register", json={"email": "reset@test.com", "password": "correctpass1"})

    #2 неудачные попытки, не доходим до лимита в 5
    client.post("/auth/login", json={"email": "reset@test.com", "password": "wrong1"})
    client.post("/auth/login", json={"email": "reset@test.com", "password": "wrong2"})

    #успешный вход должен сбросить счетчик
    response = client.post(
        "/auth/login", json={"email": "reset@test.com", "password": "correctpass1"}
    )
    assert response.status_code == 200


def test_weak_password_rejected(client):
    response = client.post(
        "/auth/register", json={"email": "weak@test.com", "password": "12345"}
    )
    assert response.status_code == 422


def test_password_without_digit_rejected(client):
    response = client.post(
        "/auth/register", json={"email": "nodigit@test.com", "password": "onlylettershere"}
    )
    assert response.status_code == 422