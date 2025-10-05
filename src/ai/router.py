from __future__ import annotations
import logging
from typing import Dict, Any, List
from .agent import SecurityAgent

logger = logging.getLogger(__name__)

class MultiAgentRouter:
    """Routes vulnerability analysis to specialized sub-agents based on type."""

    def __init__(self, base_agent: SecurityAgent) -> None:
        self.base_agent = base_agent
        self.specialized_agents = {
            "sql_injection": self._sql_agent,
            "ssti": self._ssti_agent,
            "hardcoded_secret": self._secret_agent,
            "missing_auth": self._auth_agent,
        }

    async def route_analysis(self, pr_url: str, detected_vulns: List[str]) -> Dict[str, Any]:
        """Route to specialized agents based on detected vulnerabilities."""
        results = {}
        for vuln in detected_vulns:
            agent_func = self.specialized_agents.get(vuln, self._default_agent)
            try:
                specialized_result = await agent_func(pr_url, vuln)
                results[vuln] = specialized_result
            except Exception as e:
                logger.error(f"Error in specialized agent for {vuln}: {e}")
                results[vuln] = {"error": str(e)}
        return results

    async def _sql_agent(self, pr_url: str, vuln: str) -> Dict[str, Any]:
        """Specialized SQL injection analysis."""
        # Enhanced prompt for SQL-specific analysis
        enhanced_input = f"Focus on SQL injection in FastAPI code: {pr_url}"
        # For now, delegate to base agent with specialized prompt
        return {"specialized": "SQL analysis", "vulnerability": vuln}

    async def _ssti_agent(self, pr_url: str, vuln: str) -> Dict[str, Any]:
        """Specialized SSTI analysis."""
        return {"specialized": "SSTI analysis", "vulnerability": vuln}

    async def _secret_agent(self, pr_url: str, vuln: str) -> Dict[str, Any]:
        """Specialized secret detection."""
        return {"specialized": "Secret analysis", "vulnerability": vuln}

    async def _auth_agent(self, pr_url: str, vuln: str) -> Dict[str, Any]:
        """Specialized auth analysis."""
        return {"specialized": "Auth analysis", "vulnerability": vuln}

    async def _default_agent(self, pr_url: str, vuln: str) -> Dict[str, Any]:
        """Default fallback agent."""
        return {"specialized": "General analysis", "vulnerability": vuln}
