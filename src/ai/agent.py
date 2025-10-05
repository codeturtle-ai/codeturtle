from __future__ import annotations
import logging
from typing import List, Dict, Any
import httpx
from tenacity import retry, stop_after_attempt, wait_exponential
from .knowledge_base import FastAPISecurityKB
from .schemas.models import VulnerabilityReport
from .router import MultiAgentRouter
from ..detection.ast_analyzer import ASTAnalyzer
from ..utils.report_generator import generate_natural_language_report

logger = logging.getLogger(__name__)

class SecurityAgent:
    def __init__(self, ai_client, github_token: str | None = None) -> None:
        self.ai_client = ai_client
        self.github_token = github_token
        self.kb = FastAPISecurityKB()
        self.router = MultiAgentRouter(self)

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
        """Analyze PR with hybrid AST + AI + RAG detection."""
        try:
            # Function calling: Fetch PR content
            code_snippet = await self.fetch_pr_diff(pr_url)
            

            # AST Analysis: Static detection
            ast_analyzer = ASTAnalyzer()
            ast_findings = ast_analyzer.analyze_code(code_snippet)

            # RAG: Retrieve relevant knowledge based on code + AST findings
            query = code_snippet + " " + " ".join([f["vulnerability"] for f in ast_findings])
            kb_context = self.kb.retrieve(query)
            context_str = "\n".join([
                f"Vulnerability: {item['vulnerability']}\nDescription: {item['description']}\nRemediation: {item['remediation']}\nSeverity: {item['severity']}"
                for item in kb_context
            ])

            # Merge AST and KB context into AI prompt
            ast_summary = "\n".join([
                f"AST Finding: {f['vulnerability']} (confidence: {f['confidence']})"
                for f in ast_findings
            ])
            enhanced_input = f"Code: {code_snippet}\n\nAST Findings:\n{ast_summary}\n\nKnowledge Base:\n{context_str}\n\nAnalyze for FastAPI security vulnerabilities."
            ai_result = await self.ai_client.analyze_code(enhanced_input)

            # Blend results: Combine AI, AST, and KB
            all_vulnerabilities = set(ai_result.get("labels", []))
            all_vulnerabilities.update([f["vulnerability"] for f in ast_findings])
            all_vulnerabilities.update([item["vulnerability"] for item in kb_context])

            # Blended risk score: Weighted by severity and confidence
            severity_weights = {"low": 0.2, "medium": 0.5, "high": 0.8, "critical": 1.0}
            ai_conf = float(ai_result.get("confidence", 0.0))

            # Weight AST findings by severity
            ast_weighted_confs = [
                f["confidence"] * severity_weights.get(f.get("severity", "medium"), 0.5)
                for f in ast_findings
            ]
            # Weight KB findings (assume medium severity if not specified)
            kb_weighted_confs = [
                0.6 * severity_weights.get(item.get("severity", "medium"), 0.5)  # Lower weight for KB
                for item in kb_context
            ]

            all_confs = [ai_conf] + ast_weighted_confs + kb_weighted_confs
            blended_score = sum(all_confs) / len(all_confs) if all_confs else 0.0

            # Multi-agent routing: Specialized analysis for detected vul
            specialized_results = await self.router.route_analysis(pr_url, list(all_vulnerabilities))

            # Combine recommendations
            recs = ai_result.get("recommendations", [])
            recs.extend([f["description"] for f in ast_findings if "description" in f])
            recs.extend([item["remediation"] for item in kb_context])
            # Add specialized recommendations
            for result in specialized_results.values():
                if isinstance(result, dict) and "recommendation" in result:
                    recs.append(result["recommendation"])

            # Generate natural-language summary
            summary = generate_natural_language_report(
                list(all_vulnerabilities), round(blended_score, 2), list(set(recs))
            )

            return VulnerabilityReport(
                pr_url=pr_url,
                vulnerabilities=list(all_vulnerabilities),
                risk_score=round(blended_score, 2),
                recommendations=list(set(recs)),  # Deduplicate
                summary=summary,
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
