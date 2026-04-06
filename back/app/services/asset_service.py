from typing import List, Optional

from sqlalchemy.orm import Session

from app.models.asset import Asset
from app.repositories.asset_repository import asset_repository
from app.schemas.asset import AssetCreate, AssetUpdate


class AssetService:
    """
    Responsável pelo gerenciamento de ativos favoritos do usuário.
    (Single Responsibility Principle)
    """

    def create(self, db: Session, data: AssetCreate, user_id: int) -> Asset:
        existing = asset_repository.get_by_symbol_and_user(db, data.symbol, user_id)
        if existing:
            raise ValueError(f"{data.symbol.upper()} já está nos seus favoritos")
        asset = Asset(
            symbol=data.symbol.upper(),
            name=data.name,
            user_id=user_id,
        )
        return asset_repository.create(db, asset)

    def get_all(self, db: Session, user_id: int) -> List[Asset]:
        return asset_repository.get_by_user(db, user_id)

    def get_by_id(self, db: Session, asset_id: int, user_id: int) -> Optional[Asset]:
        return asset_repository.get_by_id_and_user(db, asset_id, user_id)

    def update(self, db: Session, asset_id: int, data: AssetUpdate, user_id: int) -> Optional[Asset]:
        asset = asset_repository.get_by_id_and_user(db, asset_id, user_id)
        if not asset:
            return None
        if data.symbol is not None:
            asset.symbol = data.symbol.upper()
        if data.name is not None:
            asset.name = data.name
        return asset_repository.update(db, asset)

    def delete(self, db: Session, asset_id: int, user_id: int) -> bool:
        asset = asset_repository.get_by_id_and_user(db, asset_id, user_id)
        if not asset:
            return False
        asset_repository.delete(db, asset)
        return True


asset_service = AssetService()
