from fastapi.testclient import TestClient


def test_register_success(client: TestClient):
    response = client.post(
        "/api/v1/auth/register",
        json={"email": "novo@example.com", "password": "senha123"},
    )
    assert response.status_code == 201
    data = response.json()
    assert data["email"] == "novo@example.com"
    assert "id" in data
    assert "hashed_password" not in data


def test_register_duplicate_email(client: TestClient, registered_user: dict):
    response = client.post(
        "/api/v1/auth/register",
        json={"email": registered_user["email"], "password": "outrasenha"},
    )
    assert response.status_code == 409


def test_login_success(client: TestClient, registered_user: dict):
    response = client.post(
        "/api/v1/auth/login",
        json={"email": registered_user["email"], "password": registered_user["password"]},
    )
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"


def test_login_invalid_password(client: TestClient, registered_user: dict):
    response = client.post(
        "/api/v1/auth/login",
        json={"email": registered_user["email"], "password": "senhaerrada"},
    )
    assert response.status_code == 401


def test_login_nonexistent_user(client: TestClient):
    response = client.post(
        "/api/v1/auth/login",
        json={"email": "naoexiste@example.com", "password": "qualquersenha"},
    )
    assert response.status_code == 401


def test_protected_route_without_token(client: TestClient):
    response = client.get("/api/v1/assets")
    assert response.status_code == 403
