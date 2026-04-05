from datetime import datetime, timezone
from typing import Optional

from sqlalchemy.orm import Session

from app.models.price_history import PriceHistory
from app.repositories.asset_repository import asset_repository
from app.repositories.price_history_repository import price_history_repository
from app.schemas.quote import QuoteResponse
from app.services.brapi_service import BrapiService


class QuoteService:
    """
    Responsável por buscar cotações na brapi e persistir o histórico.
    Dependency Inversion: depende da abstração BrapiService, não de uma implementação concreta.
    """

    def __init__(self, brapi: BrapiService) -> None:
        self._brapi = brapi

    def get_quote(
        self, db: Session, symbol: str, asset_id: Optional[int] = None
    ) -> Optional[QuoteResponse]:
        data = self._brapi.get_quote(symbol)
        if not data:
            return None

        price = data.get("regularMarketPrice")
        change_percent = data.get("regularMarketChangePercent")

        if price is not None and asset_id is not None:
            self._persist_history(
                db,
                asset_id=asset_id,
                symbol=symbol,
                price=price,
                change_percent=change_percent,
                volume=data.get("regularMarketVolume"),
            )

        return QuoteResponse(
            symbol=symbol.upper(),
            shortName=data.get("shortName"),
            regularMarketPrice=price,
            regularMarketChangePercent=change_percent,
            regularMarketVolume=data.get("regularMarketVolume"),
            regularMarketPreviousClose=data.get("regularMarketPreviousClose"),
            logourl=data.get("logourl"),
        )

    def get_history(self, db: Session, symbol: str) -> list:
        """
        Tenta buscar histórico fresco na brapi.
        Caso falhe, retorna o histórico persistido no banco.
        """
        fresh = self._brapi.get_history(symbol)
        if fresh:
            return fresh
        return price_history_repository.get_by_symbol(db, symbol)

    def refresh_all_assets(self, db: Session) -> None:
        """
        Atualiza as cotações de todos os ativos cadastrados no sistema.
        Agrupa por símbolo para evitar chamadas redundantes à API.
        """
        all_assets = asset_repository.get_all(db)

        symbol_to_assets: dict[str, list] = {}
        for asset in all_assets:
            symbol_to_assets.setdefault(asset.symbol, []).append(asset)

        for symbol, assets in symbol_to_assets.items():
            data = self._brapi.get_quote(symbol)
            if not data:
                continue

            price = data.get("regularMarketPrice")
            change_percent = data.get("regularMarketChangePercent")
            volume = data.get("regularMarketVolume")

            if price is None:
                continue

            for asset in assets:
                self._persist_history(db, asset.id, symbol, price, change_percent, volume)

    def _persist_history(
        self,
        db: Session,
        asset_id: int,
        symbol: str,
        price: float,
        change_percent: Optional[float],
        volume: Optional[float],
    ) -> None:
        record = PriceHistory(
            asset_id=asset_id,
            symbol=symbol.upper(),
            price=price,
            change_percent=change_percent,
            volume=volume,
            fetched_at=datetime.now(timezone.utc),
        )
        price_history_repository.create(db, record)


quote_service = QuoteService(brapi=BrapiService())
