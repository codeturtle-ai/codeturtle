# Comprehensive Testing Suite for FastAPI Security Agent

import pytest
import asyncio
from unittest.mock import AsyncMock, MagicMock, patch
from fastapi.testclient import TestClient
from src.main import app
from src.clients.gradient_ai import GradientAIClient
from src.ai.agent import SecurityAgent
from src.schemas.models import PRAnalysisRequest

# Test client for FastAPI
client = TestClient(app)

class TestFastAPISecurityAgent:
    
    @pytest.fixture
    def mock_ai_client(self):
        """Mock AI client for testing."""
        mock_client = MagicMock(spec=GradientAIClient)
        mock_client.analyze_code = AsyncMock(return_value={
            'labels': ['sql_injection'],
            'confidence': 0.8,
            'recommendations': ['Use parameterized queries']
        })
        return mock_client
    
    @pytest.fixture
    def mock_agent(self, mock_ai_client):
        """Mock security agent."""
        return SecurityAgent(ai_client=mock_ai_client, github_token=None)
    
    def test_root_endpoint(self):
        """Test root endpoint returns correct info."""
        response = client.get('/')
        assert response.status_code == 200
        data = response.json()
        assert 'FastAPI Security Agent' in data['message']
        assert 'endpoints' in data
    
    def test_health_endpoint(self):
        """Test health check endpoint."""
        response = client.get('/health')
        assert response.status_code == 200
        data = response.json()
        assert data['status'] == 'healthy'
        assert 'version' in data
    
    @patch('src.ai.agent.SecurityAgent.analyze_pull_request')
    def test_analyze_endpoint_success(self, mock_analyze):
        """Test successful PR analysis."""
        mock_analyze.return_value = MagicMock()
        mock_analyze.return_value.dict.return_value = {
            'pr_url': 'https://github.com/test/repo/pull/1',
            'vulnerabilities': ['sql_injection'],
            'risk_score': 0.8,
            'recommendations': ['Use parameterized queries'],
            'summary': 'Analysis complete'
        }
        
        response = client.post('/analyze', json={
            'url': 'https://github.com/test/repo/pull/1'
        })
        assert response.status_code == 200
        data = response.json()
        assert 'vulnerabilities' in data
        assert 'risk_score' in data
    
    def test_analyze_endpoint_invalid_url(self):
        """Test analysis with invalid URL."""
        response = client.post('/analyze', json={'url': 'invalid-url'})
        assert response.status_code == 422  # Pydantic validation error
    
    @patch('src.ai.agent.SecurityAgent.analyze_pull_request')
    def test_scan_endpoint(self, mock_analyze):
        """Test batch scanning endpoint."""
        mock_analyze.return_value = MagicMock()
        mock_analyze.return_value.dict.return_value = {
            'pr_url': 'https://github.com/test/repo/pull/1',
            'vulnerabilities': ['sql_injection'],
            'risk_score': 0.8,
            'recommendations': ['Fix SQL injection'],
            'summary': 'Analysis complete'
        }
        
        response = client.post('/scan', json={
            'urls': ['https://github.com/test/repo/pull/1']
        })
        assert response.status_code == 200
        data = response.json()
        assert 'results' in data
        assert len(data['results']) == 1
    
    def test_rate_limiting(self):
        """Test rate limiting works."""
        # This would require multiple rapid requests
        # For now, just ensure limiter is configured
        assert hasattr(app.state, 'limiter')
    
    # Integration tests
    @pytest.mark.asyncio
    async def test_agent_initialization(self, mock_ai_client):
        """Test agent initializes correctly."""
        agent = SecurityAgent(ai_client=mock_ai_client, github_token='test_token')
        assert agent.ai_client == mock_ai_client
        assert agent.github_token == 'test_token'
        assert agent.kb is not None
        assert agent.router is not None
    
    @pytest.mark.asyncio
    async def test_ai_client_fallback(self):
        """Test AI client fallback when no API key."""
        client = GradientAIClient(api_key=None)
        result = await client.analyze_code('test code')
        assert 'labels' in result
        assert result['confidence'] > 0
    
    @pytest.mark.asyncio
    async def test_kb_retrieval(self):
        """Test knowledge base retrieval."""
        from src.ai.knowledge_base import FastAPISecurityKB
        kb = FastAPISecurityKB()
        results = kb.retrieve('SELECT * FROM users')
        assert len(results) > 0
        assert any('sql_injection' in item['vulnerability'] for item in results)

if __name__ == '__main__':
    pytest.main([__file__, '-v'])
