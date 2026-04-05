from typing import List, Optional

from sqlalchemy.orm import Session

from app.models.price_history import PriceHistory
from app.repositories.base import BaseRepository


class PriceHistoryRepository(BaseRepository[PriceHistory]):
    def __init__(self) -> None:
        super().__init__(PriceHistory)

    def get_by_symbol(self, db: Session, symbol: str, limit: int = 60) -> List[PriceHistory]:
        return (
            db.query(PriceHistory)
            .filter(PriceHistory.symbol == symbol.upper())
            .order_by(PriceHistory.fetched_at.asc())
            .limit(limit)
            .all()
        )

    def get_latest_by_symbol(self, db: Session, symbol: str) -> Optional[PriceHistory]:
        return (
            db.query(PriceHistory)
            .filter(PriceHistory.symbol == symbol.upper())
            .order_by(PriceHistory.fetched_at.desc())
            .first()
        )

    def get_latest_by_asset_id(self, db: Session, asset_id: int) -> Optional[PriceHistory]:
        return (
            db.query(PriceHistory)
            .filter(PriceHistory.asset_id == asset_id)
            .order_by(PriceHistory.fetched_at.desc())
            .first()
        )


price_history_repository = PriceHistoryRepository()
