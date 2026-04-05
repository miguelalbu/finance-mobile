from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.v1.router import router
from app.core.config import settings
from app.core.scheduler import create_scheduler
from app.db.base import Base
from app.db.session import SessionLocal, engine
from app.services.quote_service import quote_service

# Importa todos os models para garantir que sejam registrados no metadata
import app.models  # noqa: F401


def _refresh_job() -> None:
    """Job executado pelo scheduler para atualizar cotações periodicamente."""
    db = SessionLocal()
    try:
        quote_service.refresh_all_assets(db)
    finally:
        db.close()


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Cria as tabelas no banco ao iniciar
    Base.metadata.create_all(bind=engine)

    scheduler = None
    if not settings.TESTING:
        scheduler = create_scheduler(_refresh_job)
        scheduler.start()

    yield

    if scheduler:
        scheduler.shutdown()


app = FastAPI(
    title="Finance API",
    description="API para consulta de cotações de ativos financeiros",
    version="1.0.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(router)


@app.get("/health", tags=["health"])
def health_check():
    return {"status": "ok"}
