from typing import List, Optional

from sqlalchemy.orm import Session

from app.models.asset import Asset
from app.repositories.price_history_repository import price_history_repository
from app.schemas.quote import HighlightResponse


class HighlightService:
    """
    Regra de destaque: o ativo favorito com MAIOR variação percentual positiva no dia.

    Critério: entre todos os ativos favoritos do usuário que possuem histórico
    de preços, o ativo em destaque é aquele cujo registro mais recente tem o
    maior `change_percent` (variação percentual em relação ao fechamento anterior).

    Caso nenhum ativo tenha dados históricos disponíveis, retorna None.
    """

    def get_highlight(self, db: Session, assets: List[Asset]) -> Optional[HighlightResponse]:
        best: Optional[HighlightResponse] = None
        best_change: Optional[float] = None

        for asset in assets:
            latest = price_history_repository.get_latest_by_asset_id(db, asset.id)
            if latest is None or latest.change_percent is None:
                continue

            # Só considera ativos com variação positiva
            if latest.change_percent <= 0:
                continue

            if best_change is None or latest.change_percent > best_change:
                best_change = latest.change_percent
                best = HighlightResponse(
                    asset_id=asset.id,
                    symbol=asset.symbol,
                    name=asset.name,
                    change_percent=latest.change_percent,
                    price=latest.price,
                )

        return best


highlight_service = HighlightService()
