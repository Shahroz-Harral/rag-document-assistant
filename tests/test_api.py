"""
RAG Document Assistant — API Tests
"""

import pytest
from httpx import AsyncClient, ASGITransport
from app.main import app


@pytest.fixture
def client():
    transport = ASGITransport(app=app)
    return AsyncClient(transport=transport, base_url="http://test")


@pytest.mark.asyncio
async def test_root(client):
    async with client as ac:
        response = await ac.get("/")
    assert response.status_code == 200
    assert "RAG Document Assistant" in response.json()["message"]


@pytest.mark.asyncio
async def test_health(client):
    async with client as ac:
        response = await ac.get("/api/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ok"
    assert "llm_provider" in data


@pytest.mark.asyncio
async def test_list_documents_empty(client):
    async with client as ac:
        response = await ac.get("/api/documents/")
    assert response.status_code == 200
    assert response.json() == []
