import pytest
from httpx import AsyncClient, ASGITransport
from typing import AsyncGenerator
from app.main import app
# CORRECCIÓN: Importamos AsyncSessionLocal, que es el nombre real en tu código
from app.db.session import AsyncSessionLocal 

# Fixture del Cliente API (Simula Postman/Frontend)
@pytest.fixture(scope="function")
async def client() -> AsyncGenerator[AsyncClient, None]:
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac

# Fixture de Base de Datos (Nos deja "tocar" la DB directamente)
@pytest.fixture(scope="function")
async def db():
    # Usamos AsyncSessionLocal para crear una sesión real
    async with AsyncSessionLocal() as session:
        yield session