from fastapi import APIRouter

from app.api.v1.endpoints import assets, auth, quotes

router = APIRouter(prefix="/api/v1")

router.include_router(auth.router)
router.include_router(assets.router)
router.include_router(quotes.router)
