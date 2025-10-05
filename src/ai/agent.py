from __future__ import annotations
import logging
from typing import List, Dict, Any, Optional
import httpx
from tenacity import retry, stop_after_attempt, wait_exponential
from .knowledge_base import FastAPISecurityKB
from ..schemas.models import VulnerabilityReport
from .router import MultiAgentRouter
from ..detection.ast_analyzer import ASTAnalyzer
from ..clients.github_client import GitHubClient
from ..utils.report_generator import generate_natural_language_report
from ..utils.scoring import RiskScorer

logger = logging.getLogger(__name__)

class SecurityAgent:
    def __init__(self, ai_client, github_token: Optional[str] = None) -> None:
        self.ai_client = ai_client
        self.github_token = github_token
        self.kb = FastAPISecurityKB()
        self.router = MultiAgentRouter(self)
        self.github_client = GitHubClient(github_token)
        self.risk_scorer = RiskScorer()  # Production-grade risk scoring

    async def fetch_pr_diff(self, pr_url: str) -> Dict[str, Any]:
        """Fetch comprehensive PR diff data from GitHub API."""
        try:
            # Use the real GitHub client to fetch PR content
            pr_data = await self.github_client.get_pr_diff_content(pr_url)
            return pr_data
        except Exception as e:
            logger.error(f"Error fetching PR diff: {str(e)}")
            # Fallback to mock data
            return {
                "pr_url": pr_url,
                "metadata": {"title": "Fallback Analysis", "error": str(e)},
                "files": [],
                "combined_code": "# Fallback mock code for analysis\npassword = 'hardcoded_secret'\nexecute('SELECT * FROM users WHERE id = ' + user_id)",
                "total_files": 0,
                "analyzable_files": 0,
                "error": str(e)
            }

    async def analyze_pull_request(self, pr_url: str) -> VulnerabilityReport:
        """Analyze PR with hybrid AST + AI + RAG detection."""
        try:
            # Function calling: Fetch comprehensive PR content
            pr_data = await self.fetch_pr_diff(pr_url)
            code_snippet = pr_data.get("combined_code", "")
            metadata = pr_data.get("metadata", {})
            
            if not code_snippet.strip():
                logger.warning(f"No analyzable code found in PR: {pr_url}")
                return VulnerabilityReport(
                    pr_url=pr_url,
                    vulnerabilities=["no_code_found"],
                    risk_score=0.0,
                    recommendations=["No analyzable code changes found in this PR"],
                    summary=f"PR '{metadata.get('title', 'Unknown')}' contains no analyzable code changes"
                )

            # AST Analysis: Static detection
            ast_analyzer = ASTAnalyzer()
            ast_findings = ast_analyzer.analyze_code(code_snippet)

            # RAG: Retrieve relevant knowledge based on code + AST findings
            query = code_snippet[:1000] + " " + " ".join([f["vulnerability"] for f in ast_findings])  # Limit query size
            kb_context = self.kb.retrieve(query)
            
            # Enhanced AI analysis with context
            enhanced_input = self._create_enhanced_prompt(code_snippet, ast_findings, kb_context, metadata)
            ai_result = await self.ai_client.analyze_code(enhanced_input)

            # Production-grade risk scoring using dedicated scorer
            ai_confidence = float(ai_result.get("confidence", 0.0))
            kb_matches = len(kb_context)
            scoring_result = self.risk_scorer.calculate_risk_score(ast_findings, ai_confidence, kb_matches)
            risk_score = scoring_result["risk_score"]
            
            logger.info(f"Risk scoring breakdown for {pr_url}: {scoring_result}")

            # Combine and deduplicate vulnerabilities
            all_vulnerabilities = self._combine_vulnerabilities(ai_result, ast_findings, kb_context)

            # Generate comprehensive recommendations using scorer
            recommendations = self.risk_scorer.get_recommendations(ast_findings, risk_score)
            # Add AI recommendations
            recommendations.extend(ai_result.get("recommendations", []))
            # Deduplicate
            recommendations = list(dict.fromkeys(recommendations))[:10]  # Keep top 10 unique

            # Generate natural language summary
            summary = generate_natural_language_report(
                list(all_vulnerabilities), 
                risk_score, 
                recommendations
            )

            return VulnerabilityReport(
                pr_url=pr_url,
                vulnerabilities=list(all_vulnerabilities),
                risk_score=round(risk_score, 2),
                recommendations=recommendations,
                summary=summary
            )
            
        except Exception as e:
            logger.error(f"Error analyzing PR {pr_url}: {str(e)}")
            # Enhanced fallback with error details
        return VulnerabilityReport(
            pr_url=pr_url,
                vulnerabilities=["analysis_error"],
                risk_score=0.0,
                recommendations=[
                    f"Analysis failed: {str(e)}",
                    "Check PR URL format and API keys",
                    "Ensure repository is public or token has access"
                ],
                summary=f"Analysis failed due to: {str(e)}"
            )
    
    def _create_enhanced_prompt(self, code: str, ast_findings: List[Dict], kb_context: List[Dict], metadata: Dict) -> str:
        """Create enhanced prompt with all available context."""
        ast_summary = "\n".join([
            f"- {f['vulnerability']} (confidence: {f['confidence']}, severity: {f.get('severity', 'unknown')})"
            for f in ast_findings
        ]) if ast_findings else "No static analysis findings"
        
        kb_summary = "\n".join([
            f"- {item['vulnerability']}: {item['description'][:100]}..."
            for item in kb_context
        ]) if kb_context else "No knowledge base matches"
        
        pr_context = f"PR Title: {metadata.get('title', 'Unknown')}\nAuthor: {metadata.get('author', 'Unknown')}"
        
        return f"""{pr_context}

Code to analyze:
{code[:2000]}{'...' if len(code) > 2000 else ''}

Static Analysis Findings:
{ast_summary}

Knowledge Base Context:
{kb_summary}

Please analyze this FastAPI-related code for security vulnerabilities."""
    
    def _calculate_advanced_risk_score(self, ai_result: Dict, ast_findings: List[Dict], 
                                     kb_context: List[Dict], pr_data: Dict) -> float:
        """Calculate sophisticated risk score based on multiple factors."""
        # Base scores from different sources
        ai_confidence = float(ai_result.get("confidence", 0.0))
        
        # Severity weights
        severity_weights = {"low": 0.25, "medium": 0.5, "high": 0.75, "critical": 1.0}
        
        # AST findings weighted by severity and confidence
        ast_score = 0.0
        if ast_findings:
            ast_scores = [
                f["confidence"] * severity_weights.get(f.get("severity", "medium"), 0.5)
                for f in ast_findings
            ]
            ast_score = max(ast_scores) if ast_scores else 0.0
        
        # Knowledge base relevance score
        kb_score = min(len(kb_context) * 0.1, 0.3)  # Cap at 0.3
        
        # PR complexity factors
        complexity_factor = 1.0
        if pr_data.get("total_additions", 0) > 100:
            complexity_factor += 0.1  # Large PRs are riskier
        if pr_data.get("analyzable_files", 0) > 5:
            complexity_factor += 0.1  # Many files are riskier
        
        # Combine scores with weights
        weighted_score = (
            ai_confidence * 0.4 +      # AI analysis gets highest weight
            ast_score * 0.35 +         # Static analysis is reliable
            kb_score * 0.15 +          # Knowledge base provides context
            (len(ai_result.get("labels", [])) * 0.1)  # Number of vulnerabilities found
        ) * complexity_factor
        
        # Normalize to 0-1 range
        return min(weighted_score, 1.0)
    
    def _combine_vulnerabilities(self, ai_result: Dict, ast_findings: List[Dict], 
                               kb_context: List[Dict]) -> set:
        """Combine and deduplicate vulnerabilities from all sources."""
        vulnerabilities = set()
        
        # Add AI-detected vulnerabilities
        vulnerabilities.update(ai_result.get("labels", []))
        
        # Add AST findings
        vulnerabilities.update([f["vulnerability"] for f in ast_findings])
        
        # Add relevant KB vulnerabilities (only if they match the code)
        for item in kb_context:
            vulnerabilities.add(item["vulnerability"])
        
        # Remove generic/error entries
        vulnerabilities.discard("analysis_error")
        vulnerabilities.discard("parsing_error")
        vulnerabilities.discard("no_code_found")
        
        return vulnerabilities
    
    def _generate_recommendations(self, ai_result: Dict, ast_findings: List[Dict], 
                                kb_context: List[Dict], pr_data: Dict) -> List[str]:
        """Generate comprehensive, actionable recommendations."""
        recommendations = []
        
        # Add AI recommendations
        recommendations.extend(ai_result.get("recommendations", []))
        
        # Add AST-specific recommendations
        for finding in ast_findings:
            if "description" in finding:
                recommendations.append(f"AST: {finding['description']}")
        
        # Add KB recommendations
        for item in kb_context:
            recommendations.append(f"Security: {item['remediation']}")
        
        # Add PR-specific recommendations
        if pr_data.get("total_additions", 0) > 100:
            recommendations.append("Consider breaking large PRs into smaller, reviewable chunks")
        
        if pr_data.get("analyzable_files", 0) > 5:
            recommendations.append("Multiple files changed - ensure consistent security practices across all files")
        
        # Deduplicate and limit
        unique_recs = list(set(recommendations))
        return unique_recs[:8]  # Limit to 8 most important recommendations


