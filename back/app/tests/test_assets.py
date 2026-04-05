from fastapi.testclient import TestClient


def test_create_asset(client: TestClient, auth_headers: dict):
    response = client.post(
        "/api/v1/assets",
        json={"symbol": "petr4", "name": "Petrobras"},
        headers=auth_headers,
    )
    assert response.status_code == 201
    data = response.json()
    assert data["symbol"] == "PETR4"  # deve ser upper-case
    assert data["name"] == "Petrobras"
    assert "id" in data
    assert "created_at" in data


def test_list_assets(client: TestClient, auth_headers: dict):
    client.post("/api/v1/assets", json={"symbol": "PETR4", "name": "Petrobras"}, headers=auth_headers)
    client.post("/api/v1/assets", json={"symbol": "VALE3", "name": "Vale"}, headers=auth_headers)

    response = client.get("/api/v1/assets", headers=auth_headers)
    assert response.status_code == 200
    assert len(response.json()) == 2


def test_get_asset_by_id(client: TestClient, auth_headers: dict):
    create = client.post(
        "/api/v1/assets", json={"symbol": "ITUB4", "name": "Itaú"}, headers=auth_headers
    )
    asset_id = create.json()["id"]

    response = client.get(f"/api/v1/assets/{asset_id}", headers=auth_headers)
    assert response.status_code == 200
    assert response.json()["symbol"] == "ITUB4"


def test_get_asset_not_found(client: TestClient, auth_headers: dict):
    response = client.get("/api/v1/assets/9999", headers=auth_headers)
    assert response.status_code == 404


def test_update_asset(client: TestClient, auth_headers: dict):
    create = client.post(
        "/api/v1/assets", json={"symbol": "PETR4", "name": "Petrobras"}, headers=auth_headers
    )
    asset_id = create.json()["id"]

    response = client.put(
        f"/api/v1/assets/{asset_id}",
        json={"name": "Petrobras Atualizado"},
        headers=auth_headers,
    )
    assert response.status_code == 200
    assert response.json()["name"] == "Petrobras Atualizado"
    assert response.json()["symbol"] == "PETR4"


def test_update_asset_symbol(client: TestClient, auth_headers: dict):
    create = client.post(
        "/api/v1/assets", json={"symbol": "PETR4", "name": "Petrobras"}, headers=auth_headers
    )
    asset_id = create.json()["id"]

    response = client.put(
        f"/api/v1/assets/{asset_id}",
        json={"symbol": "petr3"},
        headers=auth_headers,
    )
    assert response.status_code == 200
    assert response.json()["symbol"] == "PETR3"


def test_delete_asset(client: TestClient, auth_headers: dict):
    create = client.post(
        "/api/v1/assets", json={"symbol": "PETR4", "name": "Petrobras"}, headers=auth_headers
    )
    asset_id = create.json()["id"]

    response = client.delete(f"/api/v1/assets/{asset_id}", headers=auth_headers)
    assert response.status_code == 204

    response = client.get(f"/api/v1/assets/{asset_id}", headers=auth_headers)
    assert response.status_code == 404


def test_assets_isolated_between_users(client: TestClient):
    client.post("/api/v1/auth/register", json={"email": "user1@test.com", "password": "123456"})
    client.post("/api/v1/auth/register", json={"email": "user2@test.com", "password": "123456"})

    token1 = client.post(
        "/api/v1/auth/login", json={"email": "user1@test.com", "password": "123456"}
    ).json()["access_token"]
    token2 = client.post(
        "/api/v1/auth/login", json={"email": "user2@test.com", "password": "123456"}
    ).json()["access_token"]

    headers1 = {"Authorization": f"Bearer {token1}"}
    headers2 = {"Authorization": f"Bearer {token2}"}

    client.post("/api/v1/assets", json={"symbol": "PETR4", "name": "Petrobras"}, headers=headers1)

    response = client.get("/api/v1/assets", headers=headers2)
    assert response.json() == []
