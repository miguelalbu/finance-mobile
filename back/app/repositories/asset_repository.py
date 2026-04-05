from typing import List, Optional

from sqlalchemy.orm import Session

from app.models.asset import Asset
from app.repositories.base import BaseRepository


class AssetRepository(BaseRepository[Asset]):
    def __init__(self) -> None:
        super().__init__(Asset)

    def get_by_user(self, db: Session, user_id: int) -> List[Asset]:
        return db.query(Asset).filter(Asset.user_id == user_id).all()

    def get_by_id_and_user(self, db: Session, asset_id: int, user_id: int) -> Optional[Asset]:
        return (
            db.query(Asset)
            .filter(Asset.id == asset_id, Asset.user_id == user_id)
            .first()
        )

    def get_all_symbols(self, db: Session) -> List[str]:
        results = db.query(Asset.symbol).distinct().all()
        return [r.symbol for r in results]


asset_repository = AssetRepository()
