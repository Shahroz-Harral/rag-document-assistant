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
    assert "RAG Document Assistant" in response.text


@pytest.mark.asyncio
async def test_health(client):
    async with client as ac:
        response = await ac.get("/api/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ok"
    assert "llm_provider" in data


@pytest.mark.asyncio
async def test_document_lifecycle(client):
    async with client as ac:
        # 1. Upload text document
        files = {"file": ("test_policy.txt", b"This is a test policy document for RAG.", "text/plain")}
        upload_resp = await ac.post("/api/documents/upload", files=files)
        assert upload_resp.status_code == 200
        upload_data = upload_resp.json()
        assert upload_data["filename"] == "test_policy.txt"
        assert upload_data["chunks_created"] > 0

        # 2. List documents
        list_resp = await ac.get("/api/documents/")
        assert list_resp.status_code == 200
        docs = list_resp.json()
        assert len(docs) >= 1
        assert any(d["filename"] == "test_policy.txt" for d in docs)

        # 3. Delete document
        del_resp = await ac.delete("/api/documents/test_policy.txt")
        assert del_resp.status_code == 200
        assert del_resp.json()["filename"] == "test_policy.txt"


@pytest.mark.asyncio
async def test_upload_markdown_file(client):
    async with client as ac:
        with open("docs/ASD_Centre_RAG_Knowledge_Base_Test.md", "rb") as f:
            content = f.read()

        files = {"file": ("ASD_Centre_RAG_Knowledge_Base_Test.md", content, "text/markdown")}
        resp = await ac.post("/api/documents/upload", files=files)
        assert resp.status_code == 200
        data = resp.json()
        assert data["filename"] == "ASD_Centre_RAG_Knowledge_Base_Test.md"
        assert data["chunks_created"] > 0


@pytest.mark.asyncio
async def test_chat_session(client):
    async with client as ac:
        payload = {"question": "What is the policy?", "top_k": 3}
        resp = await ac.post("/api/chat/", json=payload)
        assert resp.status_code == 200
        data = resp.json()
        assert "answer" in data
        assert "session_id" in data
        assert data["session_id"] is not None
