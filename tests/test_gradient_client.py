import pytest
from unittest.mock import AsyncMock, MagicMock
from src.clients.gradient_ai import GradientAIClient

@pytest.mark.asyncio
async def test_gradient_ai_client_no_key():
    client = GradientAIClient(api_key=None)
    result = await client.analyze_code("test code")
    assert "labels" in result
    assert result["confidence"] == 0.82

@pytest.mark.asyncio
async def test_gradient_ai_client_with_key():
    client = GradientAIClient(api_key="test_key")
    client._make_request = AsyncMock(return_value={
        "vulnerabilities": ["sql_injection"],
        "confidence": 0.9,
        "recommendations": ["Use params"]
    })
    result = await client.analyze_code("SELECT * FROM users")
    assert result["labels"] == ["sql_injection"]
    assert result["confidence"] == 0.9
