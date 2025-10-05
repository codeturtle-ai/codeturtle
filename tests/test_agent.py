import pytest
from unittest.mock import AsyncMock, MagicMock
from src.ai.agent import SecurityAgent
from src.schemas.models import VulnerabilityReport

@pytest.mark.asyncio
async def test_security_agent_analyze():
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
    assert "sql_injection" in report.vulnerabilities
    assert report.risk_score == 0.8

@pytest.mark.asyncio
async def test_security_agent_error():
    mock_client = MagicMock()
    mock_client.analyze_code = AsyncMock(side_effect=Exception("API error"))
    agent = SecurityAgent(mock_client, github_token=None)
    report = await agent.analyze_pull_request("invalid_url")
    assert report.vulnerabilities == ["analysis_error"]
    assert report.risk_score == 0.0
