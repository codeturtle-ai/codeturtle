import pytest
from unittest.mock import AsyncMock, MagicMock
from src.ai.agent import SecurityAgent
from src.schemas.models import VulnerabilityReport

@pytest.mark.asyncio
async def test_full_agent_pipeline():
    """Integration test: Full agent analysis with mocks."""
    mock_client = MagicMock()
    mock_client.analyze_code = AsyncMock(return_value={
        "labels": ["sql_injection"],
        "confidence": 0.8,
        "recommendations": ["Use params"]
    })

    agent = SecurityAgent(mock_client, github_token=None)
    report = await agent.analyze_pull_request("https://github.com/test/repo/pull/1")

    assert isinstance(report, VulnerabilityReport)
    assert report.pr_url == "https://github.com/test/repo/pull/1"
    assert len(report.vulnerabilities) > 0  # Should include AST + AI + KB findings
    assert report.risk_score > 0
    assert len(report.recommendations) > 0

@pytest.mark.asyncio
async def test_agent_with_specialized_routing():
    """Test multi-agent routing integration."""
    mock_client = MagicMock()
    mock_client.analyze_code = AsyncMock(return_value={
        "labels": ["sql_injection", "hardcoded_secret"],
        "confidence": 0.9,
        "recommendations": ["Secure queries"]
    })

    agent = SecurityAgent(mock_client, github_token=None)
    report = await agent.analyze_pull_request("https://github.com/test/repo/pull/1")

    # Check that router was called (via specialized results)
    assert isinstance(report, VulnerabilityReport)
    # Specialized agents should add to recommendations
    assert any("analysis" in rec.lower() for rec in report.recommendations)
