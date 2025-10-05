from __future__ import annotations
from typing import List
from .schemas.models import VulnerabilityReport

class SecurityAgent:
    def __init__(self, ai_client) -> None:
        self.ai_client = ai_client

    async def analyze_pull_request(self, pr_url: str) -> VulnerabilityReport:
        # TODO: fetch PR diff/content via GitHub API, for now use placeholder code
        mock_code = "SELECT * FROM users WHERE id = '1';"  # placeholder
        ai_result = await self.ai_client.analyze_code(mock_code)

        vulnerabilities = ai_result.get("labels", [])
        risk_score = float(ai_result.get("confidence", 0.0))
        recs = ai_result.get("recommendations", [])

        return VulnerabilityReport(
            pr_url=pr_url,
            vulnerabilities=[str(v) for v in vulnerabilities],
            risk_score=risk_score,
            recommendations=[str(r) for r in recs],
        )
