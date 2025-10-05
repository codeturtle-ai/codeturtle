from __future__ import annotations
import logging
from typing import List, Dict, Any
import httpx
from tenacity import retry, stop_after_attempt, wait_exponential
from .knowledge_base import FastAPISecurityKB
from .schemas.models import VulnerabilityReport

logger = logging.getLogger(__name__)

class SecurityAgent:
    def __init__(self, ai_client, github_token: str | None = None) -> None:
        self.ai_client = ai_client
        self.github_token = github_token
        self.kb = FastAPISecurityKB()

    async def fetch_pr_diff(self, pr_url: str) -> str:
        """Function calling: Fetch PR diff from GitHub API."""
        if not self.github_token:
            logger.warning("No GitHub token; using mock diff")
            return "SELECT * FROM users WHERE id = '1'; -- Mock vulnerable code"

        # Parse PR URL to extract owner/repo/pr_number
        try:
            parts = pr_url.rstrip('/').split('/')
            owner, repo, _, pr_number = parts[-4:]
        except ValueError:
            raise ValueError("Invalid PR URL format")

        url = f"https://api.github.com/repos/{owner}/{repo}/pulls/{pr_number}"
        headers = {"Authorization": f"Bearer {self.github_token}"} if self.github_token else {}

        async with httpx.AsyncClient() as client:
            resp = await client.get(url, headers=headers)
            resp.raise_for_status()
            pr_data = resp.json()
            # For simplicity, return diff_url or body; in reality, fetch the actual diff
            return pr_data.get("body", "No diff available")  # Placeholder

    async def analyze_pull_request(self, pr_url: str) -> VulnerabilityReport:
        """Analyze PR with RAG and AI."""
        try:
            # Function calling: Fetch PR content
            code_snippet = await self.fetch_pr_diff(pr_url)

            # RAG: Retrieve relevant knowledge
            kb_context = self.kb.retrieve(code_snippet)
            context_str = "\n".join([
                f"Vulnerability: {item['vulnerability']}\nDescription: {item['description']}\nRemediation: {item['remediation']}\nSeverity: {item['severity']}"
                for item in kb_context
            ])

            # Enhance AI prompt with context for deterministic responses
            enhanced_input = f"Code: {code_snippet}\n\nKnowledge Base:\n{context_str}\n\nAnalyze for FastAPI security vulnerabilities."
            ai_result = await self.ai_client.analyze_code(enhanced_input)

            vulnerabilities = ai_result.get("labels", [])
            risk_score = float(ai_result.get("confidence", 0.0))
            recs = ai_result.get("recommendations", [])

            return VulnerabilityReport(
                pr_url=pr_url,
                vulnerabilities=[str(v) for v in vulnerabilities],
                risk_score=risk_score,
                recommendations=[str(r) for r in recs],
            )
        except Exception as e:
            logger.error(f"Error analyzing PR {pr_url}: {str(e)}")
            # Fallback
            return VulnerabilityReport(
                pr_url=pr_url,
                vulnerabilities=["analysis_error"],
                risk_score=0.0,
                recommendations=["Check PR URL and API keys"],
            )
