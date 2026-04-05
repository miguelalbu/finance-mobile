import os

# Deve ser definido ANTES de qualquer import do app para que
# pydantic-settings leia as variáveis corretas ao inicializar.
os.environ.setdefault("DATABASE_URL", "sqlite:///./test.db")
os.environ.setdefault("SECRET_KEY", "test-secret-key-for-testing-only")
os.environ.setdefault("TESTING", "true")

import pytest
from fastapi.testclient import TestClient

from app.db.base import Base
from app.db.session import SessionLocal, engine, get_db
from app.main import app


@pytest.fixture(scope="function")
def reset_db():
    """Garante banco limpo: dropa tudo, recria, e dropa no fim."""
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)


@pytest.fixture(scope="function")
def db(reset_db):
    """Sessão isolada por teste."""
    session = SessionLocal()
    try:
        yield session
    finally:
        session.close()


@pytest.fixture(scope="function")
def client(db):
    """
    TestClient que compartilha a mesma sessão do fixture db.
    Isso garante que dados inseridos via API e via db sejam visíveis
    nos dois lados sem precisar de commits extras.
    """
    def override_get_db():
        try:
            yield db
        finally:
            pass

    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as c:
        yield c
    app.dependency_overrides.clear()


@pytest.fixture
def registered_user(client: TestClient) -> dict:
    response = client.post(
        "/api/v1/auth/register",
        json={"email": "test@example.com", "password": "senha123"},
    )
    assert response.status_code == 201
    return {"email": "test@example.com", "password": "senha123"}


@pytest.fixture
def auth_headers(client: TestClient, registered_user: dict) -> dict:
    response = client.post(
        "/api/v1/auth/login",
        json={"email": registered_user["email"], "password": registered_user["password"]},
    )
    token = response.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}
