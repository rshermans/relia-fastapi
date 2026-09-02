"""
Fixtures partilhadas para todos os testes do RELIA 2.0 Agêntico.
Configura base de dados SQLite in-memory, TestClient FastAPI e utilizadores de teste.

Nota: O `main.py` cria tabelas no engine global ao importar, mas os testes
usam uma BD in-memory isolada. Por isso fazemos o create_all no engine de teste
e injectamos get_db para apontar para essa BD.
"""

import pytest
from unittest.mock import patch
from sqlalchemy import create_engine, event
from sqlalchemy.pool import StaticPool
from sqlalchemy.orm import sessionmaker
from fastapi.testclient import TestClient


# ─────────────────────────────────────────────
# Fixtures de Base de Dados In-Memory
# ─────────────────────────────────────────────

@pytest.fixture(scope="function")
def db_engine():
    """Cria engine SQLite in-memory isolada por teste."""
    import backend.app.database.models  # Garante registo dos modelos nos metadados
    from backend.app.database.session import Base

    engine = create_engine(
        "sqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    Base.metadata.create_all(bind=engine)
    yield engine
    Base.metadata.drop_all(bind=engine)
    engine.dispose()


@pytest.fixture(scope="function")
def db_session(db_engine):
    """Sessão de BD isolada — rollback automático no final do teste."""
    TestingSession = sessionmaker(bind=db_engine, autocommit=False, autoflush=False)
    session = TestingSession()
    try:
        yield session
    finally:
        session.rollback()
        session.close()


# ─────────────────────────────────────────────
# TestClient FastAPI com override de get_db
# ─────────────────────────────────────────────

@pytest.fixture(scope="function")
def client(db_engine):
    """TestClient FastAPI com BD in-memory injectada."""
    from backend.app.database.session import get_db
    from backend.app.main import app

    TestingSession = sessionmaker(bind=db_engine, autocommit=False, autoflush=False)

    def _override_get_db():
        db = TestingSession()
        try:
            yield db
        finally:
            db.close()

    app.dependency_overrides[get_db] = _override_get_db
    with TestClient(app, raise_server_exceptions=True) as c:
        yield c
    app.dependency_overrides.clear()


# ─────────────────────────────────────────────
# Fixtures de Utilizadores
# ─────────────────────────────────────────────

@pytest.fixture(scope="function")
def registered_user(client):
    """Regista um utilizador de teste e retorna os dados."""
    user_data = {
        "nome": "Leitor Teste",
        "email": "teste@relia.pt",
        "password": "senhaSegura123",
        "idade": 17,
        "cidade": "Braga",
        "interesses": "Literatura, Filosofia",
        "nivel_educacional": "12º Ano",
        "habito_leitura": "Semanal",
    }
    response = client.post("/api/auth/register", json=user_data)
    assert response.status_code == 200, f"Registo falhou: {response.text}"
    return {**user_data, **response.json()}


@pytest.fixture(scope="function")
def auth_token(client, registered_user):
    """Token JWT válido para autenticação nos endpoints protegidos."""
    response = client.post(
        "/api/auth/login",
        json={"email": registered_user["email"], "password": "senhaSegura123"},
    )
    assert response.status_code == 200, f"Login falhou: {response.text}"
    token = response.json()["access_token"]
    return token


@pytest.fixture(scope="function")
def auth_headers(auth_token):
    """Headers HTTP com Bearer token para requests autenticados."""
    return {"Authorization": f"Bearer {auth_token}"}


# ─────────────────────────────────────────────
# Fixtures de Seed (usa engine de teste)
# ─────────────────────────────────────────────

@pytest.fixture(scope="function")
def seeded_db(db_engine):
    """Executa o seed da BD no engine de teste (in-memory).

    Patcha SessionLocal e engine no módulo seed_database para que use a BD de teste.
    """
    from sqlalchemy.orm import sessionmaker as _sm
    from backend.app.database import seed_database

    TestingSession = _sm(bind=db_engine, autocommit=False, autoflush=False)

    with patch.object(seed_database, "SessionLocal", TestingSession), \
         patch.object(seed_database, "engine", db_engine):
        seed_database.seed()

    return True
