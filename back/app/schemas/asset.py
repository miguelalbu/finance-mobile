from datetime import datetime
from typing import Optional
from pydantic import BaseModel


class AssetCreate(BaseModel):
    symbol: str
    name: str


class AssetUpdate(BaseModel):
    symbol: Optional[str] = None
    name: Optional[str] = None


class AssetResponse(BaseModel):
    id: int
    symbol: str
    name: str
    user_id: int
    created_at: datetime

    model_config = {"from_attributes": True}
