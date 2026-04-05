from datetime import datetime, timezone
from unittest.mock import patch

from fastapi.testclient import TestClient

MOCK_QUOTE_DATA = {
    "symbol": "PETR4",
    "shortName": "PETROBRAS PN",
    "regularMarketPrice": 38.50,
    "regularMarketChangePercent": 1.25,
    "regularMarketVolume": 1_000_000,
    "regularMarketPreviousClose": 37.80,
    "logourl": "https://example.com/logo.png",
}

MOCK_HISTORY_DATA = [
    {"date": 1700000000, "close": 37.00, "changePercent": 0.50},
    {"date": 1700086400, "close": 37.50, "changePercent": 1.35},
    {"date": 1700172800, "close": 38.50, "changePercent": 2.67},
]


def test_get_quote_success(client: TestClient, auth_headers: dict):
    client.post("/api/v1/assets", json={"symbol": "PETR4", "name": "Petrobras"}, headers=auth_headers)

    with patch("app.services.quote_service.quote_service._brapi.get_quote", return_value=MOCK_QUOTE_DATA):
        response = client.get("/api/v1/quotes/PETR4", headers=auth_headers)

    assert response.status_code == 200
    data = response.json()
    assert data["symbol"] == "PETR4"
    assert data["regularMarketPrice"] == 38.50
    assert data["regularMarketChangePercent"] == 1.25


def test_get_quote_persists_history(client: TestClient, auth_headers: dict, db):
    from app.models.price_history import PriceHistory

    create = client.post(
        "/api/v1/assets", json={"symbol": "PETR4", "name": "Petrobras"}, headers=auth_headers
    )
    asset_id = create.json()["id"]

    with patch("app.services.quote_service.quote_service._brapi.get_quote", return_value=MOCK_QUOTE_DATA):
        client.get("/api/v1/quotes/PETR4", headers=auth_headers)

    records = db.query(PriceHistory).filter_by(asset_id=asset_id).all()
    assert len(records) == 1
    assert records[0].price == 38.50


def test_get_quote_not_found(client: TestClient, auth_headers: dict):
    with patch("app.services.quote_service.quote_service._brapi.get_quote", return_value=None):
        response = client.get("/api/v1/quotes/XXXX99", headers=auth_headers)

    assert response.status_code == 404


def test_get_history_from_brapi(client: TestClient, auth_headers: dict):
    client.post("/api/v1/assets", json={"symbol": "PETR4", "name": "Petrobras"}, headers=auth_headers)

    with patch(
        "app.services.quote_service.quote_service._brapi.get_history",
        return_value=MOCK_HISTORY_DATA,
    ):
        response = client.get("/api/v1/quotes/PETR4/history", headers=auth_headers)

    assert response.status_code == 200
    data = response.json()
    assert len(data) == 3
    assert data[0]["price"] == 37.00
    assert data[1]["price"] == 37.50


def test_get_history_fallback_to_db(client: TestClient, auth_headers: dict, db):
    from app.models.price_history import PriceHistory

    create = client.post(
        "/api/v1/assets", json={"symbol": "VALE3", "name": "Vale"}, headers=auth_headers
    )
    asset_id = create.json()["id"]

    record = PriceHistory(
        asset_id=asset_id,
        symbol="VALE3",
        price=75.00,
        change_percent=0.8,
        fetched_at=datetime.now(timezone.utc),
    )
    db.add(record)
    db.commit()

    with patch(
        "app.services.quote_service.quote_service._brapi.get_history",
        return_value=[],
    ):
        response = client.get("/api/v1/quotes/VALE3/history", headers=auth_headers)

    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    assert data[0]["price"] == 75.00


def test_get_history_not_found(client: TestClient, auth_headers: dict):
    with patch(
        "app.services.quote_service.quote_service._brapi.get_history",
        return_value=[],
    ):
        response = client.get("/api/v1/quotes/XXXX99/history", headers=auth_headers)

    assert response.status_code == 404


def test_get_quote_external_api_error(client: TestClient, auth_headers: dict):
    """Garante que erro na API externa retorna 404, não 500."""
    with patch("app.services.quote_service.quote_service._brapi.get_quote", return_value=None):
        response = client.get("/api/v1/quotes/PETR4", headers=auth_headers)

    assert response.status_code == 404
