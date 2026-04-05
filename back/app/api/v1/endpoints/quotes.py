from datetime import datetime, timezone
from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api.deps import get_current_user, get_db
from app.models.user import User
from app.repositories.price_history_repository import price_history_repository
from app.schemas.quote import HighlightResponse, PriceHistoryPoint, QuoteResponse
from app.services.asset_service import asset_service
from app.services.highlight_service import highlight_service
from app.services.quote_service import quote_service

router = APIRouter(prefix="/quotes", tags=["quotes"])


@router.get("/highlight", response_model=HighlightResponse)
def get_highlight(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    assets = asset_service.get_all(db, current_user.id)
    highlight = highlight_service.get_highlight(db, assets)
    if not highlight:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Nenhum ativo com dados disponíveis para destaque",
        )
    return highlight


@router.get("/{symbol}", response_model=QuoteResponse)
def get_quote(
    symbol: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    assets = asset_service.get_all(db, current_user.id)
    user_asset = next((a for a in assets if a.symbol == symbol.upper()), None)
    asset_id = user_asset.id if user_asset else None

    quote = quote_service.get_quote(db, symbol, asset_id=asset_id)
    if not quote:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Cotação não encontrada para {symbol.upper()}",
        )
    return quote


@router.get("/{symbol}/history", response_model=List[PriceHistoryPoint])
def get_history(
    symbol: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    history = quote_service.get_history(db, symbol)
    if not history:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Histórico não disponível para {symbol.upper()}",
        )

    # Histórico vindo da brapi é uma lista de dicts; do banco é uma lista de ORM objects
    if isinstance(history[0], dict):
        return [
            PriceHistoryPoint(
                price=h.get("close") or h.get("regularMarketPrice") or 0.0,
                change_percent=h.get("changePercent"),
                fetched_at=datetime.fromtimestamp(h["date"], tz=timezone.utc)
                if h.get("date")
                else datetime.now(timezone.utc),
            )
            for h in history
        ]

    return history
