from datetime import datetime
from typing import Optional
from pydantic import BaseModel


class QuoteResponse(BaseModel):
    symbol: str
    shortName: Optional[str] = None
    regularMarketPrice: Optional[float] = None
    regularMarketChangePercent: Optional[float] = None
    regularMarketVolume: Optional[float] = None
    regularMarketPreviousClose: Optional[float] = None
    logourl: Optional[str] = None


class PriceHistoryPoint(BaseModel):
    price: float
    change_percent: Optional[float] = None
    fetched_at: datetime

    model_config = {"from_attributes": True}


class HighlightResponse(BaseModel):
    asset_id: int
    symbol: str
    name: str
    change_percent: float
    price: float
