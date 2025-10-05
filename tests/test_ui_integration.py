import pytest
from httpx import AsyncClient
from src.main import app

@pytest.mark.asyncio
async def test_ui_endpoints():
    """Integration test for UI endpoints."""
    async with AsyncClient(app=app, base_url="http://testserver") as client:
        # Test root
        resp = await client.get("/")
        assert resp.status_code == 200
        data = resp.json()
        assert "FastAPI Security Agent" in data["message"]
        assert "/ui" in data["endpoints"]

        # Test health
        resp = await client.get("/health")
        assert resp.status_code == 200
        assert resp.json()["status"] == "healthy"

        # Test UI home
        resp = await client.get("/ui")
        assert resp.status_code == 200
        assert "FastAPI Security Agent" in resp.text

        # Test report summary
        resp = await client.get("/report")
        assert resp.status_code == 200
        data = resp.json()
        assert data["type"] == "summary"
        assert "vulnerabilities_found" in data
