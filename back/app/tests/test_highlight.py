from datetime import datetime, timezone
from unittest.mock import MagicMock

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.core.security import hash_password
from app.models.asset import Asset
from app.models.price_history import PriceHistory
from app.models.user import User
from app.services.brapi_service import BrapiService
from app.services.highlight_service import HighlightService
from app.services.quote_service import QuoteService


# ─── Testes unitários do HighlightService ────────────────────────────────────

def test_highlight_returns_asset_with_highest_change(db: Session):
    user = User(email="h@test.com", hashed_password=hash_password("123"))
    db.add(user)
    db.commit()

    asset1 = Asset(symbol="PETR4", name="Petrobras", user_id=user.id)
    asset2 = Asset(symbol="VALE3", name="Vale", user_id=user.id)
    db.add_all([asset1, asset2])
    db.commit()

    db.add(PriceHistory(asset_id=asset1.id, symbol="PETR4", price=38.50, change_percent=1.25, fetched_at=datetime.now(timezone.utc)))
    db.add(PriceHistory(asset_id=asset2.id, symbol="VALE3", price=75.00, change_percent=3.10, fetched_at=datetime.now(timezone.utc)))
    db.commit()

    service = HighlightService()
    result = service.get_highlight(db, [asset1, asset2])

    assert result is not None
    assert result.symbol == "VALE3"
    assert result.change_percent == 3.10


def test_highlight_no_assets_returns_none(db: Session):
    service = HighlightService()
    result = service.get_highlight(db, [])
    assert result is None


def test_highlight_no_history_returns_none(db: Session):
    user = User(email="h2@test.com", hashed_password=hash_password("123"))
    db.add(user)
    db.commit()

    asset = Asset(symbol="ITUB4", name="Itaú", user_id=user.id)
    db.add(asset)
    db.commit()

    service = HighlightService()
    result = service.get_highlight(db, [asset])
    assert result is None


def test_highlight_all_negative_returns_none(db: Session):
    user = User(email="h4@test.com", hashed_password=hash_password("123"))
    db.add(user)
    db.commit()

    asset1 = Asset(symbol="BBAS3", name="Banco do Brasil", user_id=user.id)
    asset2 = Asset(symbol="MGLU3", name="Magazine Luiza", user_id=user.id)
    db.add_all([asset1, asset2])
    db.commit()

    db.add(PriceHistory(asset_id=asset1.id, symbol="BBAS3", price=50.00, change_percent=-0.50, fetched_at=datetime.now(timezone.utc)))
    db.add(PriceHistory(asset_id=asset2.id, symbol="MGLU3", price=10.00, change_percent=-1.50, fetched_at=datetime.now(timezone.utc)))
    db.commit()

    service = HighlightService()
    result = service.get_highlight(db, [asset1, asset2])

    assert result is None


def test_highlight_ignores_negative_if_positive_exists(db: Session):
    user = User(email="h3@test.com", hashed_password=hash_password("123"))
    db.add(user)
    db.commit()

    asset1 = Asset(symbol="BBAS3", name="Banco do Brasil", user_id=user.id)
    asset2 = Asset(symbol="MGLU3", name="Magazine Luiza", user_id=user.id)
    db.add_all([asset1, asset2])
    db.commit()

    db.add(PriceHistory(asset_id=asset1.id, symbol="BBAS3", price=50.00, change_percent=2.00, fetched_at=datetime.now(timezone.utc)))
    db.add(PriceHistory(asset_id=asset2.id, symbol="MGLU3", price=10.00, change_percent=-1.50, fetched_at=datetime.now(timezone.utc)))
    db.commit()

    service = HighlightService()
    result = service.get_highlight(db, [asset1, asset2])

    assert result is not None
    assert result.symbol == "BBAS3"


# ─── Testes do endpoint de highlight ─────────────────────────────────────────

def test_highlight_endpoint_returns_best_asset(client: TestClient, auth_headers: dict, db: Session):
    r1 = client.post("/api/v1/assets", json={"symbol": "PETR4", "name": "Petrobras"}, headers=auth_headers)
    r2 = client.post("/api/v1/assets", json={"symbol": "VALE3", "name": "Vale"}, headers=auth_headers)

    db.add(PriceHistory(asset_id=r1.json()["id"], symbol="PETR4", price=38.50, change_percent=1.25, fetched_at=datetime.now(timezone.utc)))
    db.add(PriceHistory(asset_id=r2.json()["id"], symbol="VALE3", price=75.00, change_percent=3.10, fetched_at=datetime.now(timezone.utc)))
    db.commit()

    response = client.get("/api/v1/quotes/highlight", headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert data["symbol"] == "VALE3"
    assert data["change_percent"] == 3.10


def test_highlight_endpoint_no_data(client: TestClient, auth_headers: dict):
    response = client.get("/api/v1/quotes/highlight", headers=auth_headers)
    assert response.status_code == 404


# ─── Teste da atualização periódica ──────────────────────────────────────────

def test_refresh_all_assets_calls_brapi_per_symbol(db: Session):
    user = User(email="refresh@test.com", hashed_password=hash_password("123"))
    db.add(user)
    db.commit()

    asset = Asset(symbol="PETR4", name="Petrobras", user_id=user.id)
    db.add(asset)
    db.commit()

    mock_brapi = MagicMock(spec=BrapiService)
    mock_brapi.get_quote.return_value = {
        "regularMarketPrice": 38.50,
        "regularMarketChangePercent": 1.25,
        "regularMarketVolume": 500_000,
    }

    service = QuoteService(brapi=mock_brapi)
    service.refresh_all_assets(db)

    mock_brapi.get_quote.assert_called_once_with("PETR4")

    history = db.query(PriceHistory).filter_by(asset_id=asset.id).all()
    assert len(history) == 1
    assert history[0].price == 38.50


def test_refresh_all_assets_deduplicates_symbols(db: Session):
    """Dois usuários com o mesmo símbolo: deve chamar a API apenas 1x."""
    user1 = User(email="u1@test.com", hashed_password=hash_password("123"))
    user2 = User(email="u2@test.com", hashed_password=hash_password("123"))
    db.add_all([user1, user2])
    db.commit()

    db.add(Asset(symbol="VALE3", name="Vale", user_id=user1.id))
    db.add(Asset(symbol="VALE3", name="Vale", user_id=user2.id))
    db.commit()

    mock_brapi = MagicMock(spec=BrapiService)
    mock_brapi.get_quote.return_value = {
        "regularMarketPrice": 75.00,
        "regularMarketChangePercent": 0.8,
        "regularMarketVolume": 300_000,
    }

    service = QuoteService(brapi=mock_brapi)
    service.refresh_all_assets(db)

    # Brapi chamada apenas 1x para o símbolo VALE3
    mock_brapi.get_quote.assert_called_once_with("VALE3")

    # Mas o histórico foi salvo para os 2 assets
    total = db.query(PriceHistory).count()
    assert total == 2
