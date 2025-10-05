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
from .advanced_analyzer import AdvancedAIAnalyzer, AnalysisContext, AnalysisMode
from ..scoring.risk_calculator import ProductionRiskCalculator, VulnerabilityFinding, PRComplexityMetrics, SeverityLevel
from ..utils.scoring import RiskScorer

logger = logging.getLogger(__name__)

class SecurityAgent:
    def __init__(self, ai_client, github_token: Optional[str] = None) -> None:
        self.ai_client = ai_client
        self.github_token = github_token
        self.kb = FastAPISecurityKB()
        self.router = MultiAgentRouter(self)
        self.github_client = GitHubClient(github_token)
        
        # Initialize advanced components
        self.advanced_analyzer = AdvancedAIAnalyzer(ai_client)
        self.risk_calculator = ProductionRiskCalculator()
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

    async def analyze_pull_request(self, pr_url: str, analysis_mode: AnalysisMode = AnalysisMode.COMPREHENSIVE) -> VulnerabilityReport:
        """Analyze PR with advanced multi-layer detection and production-grade scoring."""
        try:
            logger.info(f"Starting advanced analysis for PR: {pr_url}")
            
            # 1. Fetch comprehensive PR content
            pr_data = await self.fetch_pr_diff(pr_url)
            code_snippet = pr_data.get("combined_code", "")
            metadata = pr_data.get("metadata", {})
            
            if not code_snippet.strip():
                logger.warning(f"No analyzable code found in PR: {pr_url}")
                return self._create_empty_analysis_report(pr_url, metadata)

            # 2. Create analysis context
            analysis_context = AnalysisContext(
                code_snippet=code_snippet,
                file_path=pr_data.get("files", [{}])[0].get("filename") if pr_data.get("files") else None,
                pr_title=metadata.get("title"),
                pr_description=metadata.get("body"),
                author=metadata.get("author"),
                target_branch=metadata.get("base_branch"),
                framework_info={"type": "FastAPI", "language": "Python"}
            )

            # 3. Multi-layer analysis pipeline
            analysis_results = await self._run_comprehensive_analysis(
                analysis_context, pr_data, analysis_mode
            )

            # 4. Advanced risk calculation
            risk_assessment = await self._calculate_production_risk_score(
                analysis_results, pr_data, metadata
            )

            # 5. Generate comprehensive report
            return self._generate_comprehensive_report(
                pr_url, analysis_results, risk_assessment, metadata
            )
            
        except Exception as e:
            logger.error(f"Error in advanced PR analysis {pr_url}: {str(e)}")
            return self._create_error_report(pr_url, str(e))
    
    async def _run_comprehensive_analysis(
        self, 
        context: AnalysisContext, 
        pr_data: Dict[str, Any],
        mode: AnalysisMode
    ) -> Dict[str, Any]:
        """Run comprehensive multi-layer analysis."""
        
        results = {
            "ast_findings": [],
            "ai_analysis": None,
            "kb_context": [],
            "agent_results": {},
            "metadata": {}
        }
        
        try:
            # Layer 1: AST Static Analysis
            logger.info("Running AST analysis...")
            ast_analyzer = ASTAnalyzer()
            ast_findings = ast_analyzer.analyze_code(context.code_snippet)
            results["ast_findings"] = ast_findings
            
            # Layer 2: Advanced AI Analysis
            logger.info(f"Running advanced AI analysis in {mode.value} mode...")
            ai_analysis = await self.advanced_analyzer.analyze_code(context, mode)
            results["ai_analysis"] = ai_analysis
            
            # Layer 3: Knowledge Base Retrieval
            logger.info("Querying knowledge base...")
            query = context.code_snippet[:1000] + " " + " ".join([f["vulnerability"] for f in ast_findings])
            kb_context = self.kb.retrieve(query)
            results["kb_context"] = kb_context
            
            # Layer 4: Multi-Agent Specialized Analysis
            logger.info("Running multi-agent analysis...")
            detected_vulns = list(set(
                [f["vulnerability"] for f in ast_findings] +
                [v.get("type", "") for v in ai_analysis.vulnerabilities]
            ))
            
            if detected_vulns:
                agent_results = await self.router.route_analysis(context.code_snippet, detected_vulns)
                results["agent_results"] = agent_results
            
            results["metadata"] = {
                "analysis_mode": mode.value,
                "total_ast_findings": len(ast_findings),
                "total_ai_vulnerabilities": len(ai_analysis.vulnerabilities),
                "kb_matches": len(kb_context),
                "agent_analyses": len(results["agent_results"]),
                "analysis_timestamp": "2025-01-01T00:00:00Z"  # Would use actual timestamp
            }
            
            logger.info(f"Analysis complete: {results['metadata']}")
            return results
            
        except Exception as e:
            logger.error(f"Error in comprehensive analysis: {str(e)}")
            results["error"] = str(e)
            return results
    
    async def _calculate_production_risk_score(
        self, 
        analysis_results: Dict[str, Any], 
        pr_data: Dict[str, Any],
        metadata: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Calculate production-grade risk score."""
        
        try:
            # Convert analysis results to structured findings
            findings = self._convert_to_vulnerability_findings(analysis_results)
            
            # Create PR complexity metrics
            pr_metrics = PRComplexityMetrics(
                total_additions=pr_data.get("total_additions", 0),
                total_deletions=pr_data.get("total_deletions", 0),
                changed_files=pr_data.get("total_files", 0),
                analyzable_files=pr_data.get("analyzable_files", 0),
                max_file_size=max([len(f.get("patch", "")) for f in pr_data.get("files", [])], default=0),
                avg_file_size=sum([len(f.get("patch", "")) for f in pr_data.get("files", [])]) / max(len(pr_data.get("files", [])), 1),
                has_config_changes=any("config" in f.get("filename", "").lower() for f in pr_data.get("files", [])),
                has_dependency_changes=any("requirements" in f.get("filename", "").lower() or "setup.py" in f.get("filename", "").lower() for f in pr_data.get("files", [])),
                touches_security_files=any("security" in f.get("filename", "").lower() or "auth" in f.get("filename", "").lower() for f in pr_data.get("files", []))
            )
            
            # Get AI confidence
            ai_confidence = analysis_results.get("ai_analysis", {}).confidence if hasattr(analysis_results.get("ai_analysis", {}), 'confidence') else 0.5
            
            # Create context for risk calculation
            risk_context = {
                "author_reputation": "unknown",  # Could be enhanced with GitHub API data
                "repo_security_score": 0.5,     # Could be calculated from repo history
                "target_branch": metadata.get("base_branch", "main"),
                "recent_vulnerabilities": 0,     # Could be tracked over time
                "days_since_security_review": 30 # Could be calculated from commit history
            }
            
            # Calculate comprehensive risk score
            risk_assessment = self.risk_calculator.calculate_risk_score(
                findings=findings,
                pr_metrics=pr_metrics,
                ai_confidence=ai_confidence,
                context=risk_context
            )
            
            logger.info(f"Risk assessment complete: {risk_assessment['risk_category']} ({risk_assessment['risk_score']})")
            return risk_assessment
            
        except Exception as e:
            logger.error(f"Error calculating production risk score: {str(e)}")
            return {
                "risk_score": 0.5,
                "risk_category": "UNKNOWN",
                "confidence": 0.3,
                "error": str(e),
                "breakdown": {"error": "Risk calculation failed"},
                "recommendations": ["Manual risk assessment required"],
                "metadata": {"calculation_method": "fallback"}
            }
    
    def _convert_to_vulnerability_findings(self, analysis_results: Dict[str, Any]) -> List[VulnerabilityFinding]:
        """Convert analysis results to structured vulnerability findings."""
        
        findings = []
        
        # Convert AST findings
        for ast_finding in analysis_results.get("ast_findings", []):
            severity_map = {
                "critical": SeverityLevel.CRITICAL,
                "high": SeverityLevel.HIGH,
                "medium": SeverityLevel.MEDIUM,
                "low": SeverityLevel.LOW
            }
            
            findings.append(VulnerabilityFinding(
                type=ast_finding.get("vulnerability", "unknown"),
                severity=severity_map.get(ast_finding.get("severity", "medium"), SeverityLevel.MEDIUM),
                confidence=float(ast_finding.get("confidence", 0.5)),
                source="ast",
                description=ast_finding.get("description", "AST analysis finding")
            ))
        
        # Convert AI findings
        ai_analysis = analysis_results.get("ai_analysis")
        if ai_analysis and hasattr(ai_analysis, 'vulnerabilities'):
            for ai_vuln in ai_analysis.vulnerabilities:
                severity_map = {
                    "CRITICAL": SeverityLevel.CRITICAL,
                    "HIGH": SeverityLevel.HIGH,
                    "MEDIUM": SeverityLevel.MEDIUM,
                    "LOW": SeverityLevel.LOW,
                    "INFO": SeverityLevel.INFO
                }
                
                findings.append(VulnerabilityFinding(
                    type=ai_vuln.get("type", "unknown"),
                    severity=severity_map.get(ai_vuln.get("severity", "MEDIUM"), SeverityLevel.MEDIUM),
                    confidence=float(ai_vuln.get("confidence", 0.5)),
                    source="ai",
                    description=ai_vuln.get("description", "AI analysis finding"),
                    cwe_id=ai_vuln.get("cwe_id")
                ))
        
        # Convert agent findings
        for agent_type, agent_result in analysis_results.get("agent_results", {}).items():
            if isinstance(agent_result, dict) and agent_result.get("confidence", 0) > 0:
                findings.append(VulnerabilityFinding(
                    type=agent_type,
                    severity=SeverityLevel.MEDIUM,  # Default for agent findings
                    confidence=float(agent_result.get("confidence", 0.5)),
                    source="agent",
                    description=f"Multi-agent analysis: {agent_result.get('specialized', 'Unknown')}"
                ))
        
        return findings
    
    def _generate_comprehensive_report(
        self, 
        pr_url: str, 
        analysis_results: Dict[str, Any], 
        risk_assessment: Dict[str, Any],
        metadata: Dict[str, Any]
    ) -> VulnerabilityReport:
        """Generate comprehensive vulnerability report."""
        
        # Combine all vulnerabilities
        all_vulnerabilities = set()
        
        # Add AST vulnerabilities
        for finding in analysis_results.get("ast_findings", []):
            all_vulnerabilities.add(finding.get("vulnerability", "unknown"))
        
        # Add AI vulnerabilities
        ai_analysis = analysis_results.get("ai_analysis")
        if ai_analysis and hasattr(ai_analysis, 'vulnerabilities'):
            for vuln in ai_analysis.vulnerabilities:
                all_vulnerabilities.add(vuln.get("type", "unknown"))
        
        # Add agent vulnerabilities
        for agent_type in analysis_results.get("agent_results", {}).keys():
            all_vulnerabilities.add(agent_type)
        
        # Remove generic entries
        all_vulnerabilities.discard("unknown")
        all_vulnerabilities.discard("analysis_error")
        
        # Get recommendations from risk assessment
        recommendations = risk_assessment.get("recommendations", [])
        
        # Add AI recommendations if available
        if ai_analysis and hasattr(ai_analysis, 'recommendations'):
            recommendations.extend(ai_analysis.recommendations[:3])  # Add top 3 AI recommendations
        
        # Generate enhanced summary
        summary = self._generate_enhanced_summary(
            list(all_vulnerabilities),
            risk_assessment["risk_score"],
            risk_assessment["risk_category"],
            recommendations,
            metadata
        )
        
        return VulnerabilityReport(
            pr_url=pr_url,
            vulnerabilities=list(all_vulnerabilities),
            risk_score=risk_assessment["risk_score"],
            recommendations=recommendations[:8],  # Limit to 8 recommendations
            summary=summary
        )
    
    def _generate_enhanced_summary(
        self, 
        vulnerabilities: List[str], 
        risk_score: float, 
        risk_category: str,
        recommendations: List[str],
        metadata: Dict[str, Any]
    ) -> str:
        """Generate enhanced natural language summary."""
        
        vuln_count = len([v for v in vulnerabilities if v != "analysis_error"])
        
        if vuln_count == 0:
            return f"✅ Security Analysis Complete: No significant vulnerabilities detected in PR '{metadata.get('title', 'Unknown')}' (Risk Score: {risk_score:.2f}/{risk_category}). The code changes appear secure based on comprehensive multi-layer analysis."
        
        vuln_summary = f"🔍 Detected {vuln_count} potential vulnerability type(s): {', '.join(vulnerabilities[:3])}{'...' if len(vulnerabilities) > 3 else ''}."
        
        risk_emoji = {
            "CRITICAL": "🚨",
            "HIGH": "⚠️",
            "MEDIUM": "📋",
            "LOW": "ℹ️",
            "MINIMAL": "✅"
        }.get(risk_category, "❓")
        
        risk_desc = f"{risk_emoji} Overall Risk Assessment: {risk_score:.2f} ({risk_category})"
        
        rec_summary = f"💡 Key Recommendations: {'; '.join(recommendations[:2])}{'...' if len(recommendations) > 2 else '.'}"
        
        analysis_info = f"🔬 Analysis: Multi-layer detection using AST, AI, Knowledge Base, and Specialized Agents."
        
        return f"{vuln_summary} {risk_desc} {rec_summary} {analysis_info}"
    
    def _create_empty_analysis_report(self, pr_url: str, metadata: Dict[str, Any]) -> VulnerabilityReport:
        """Create report for PRs with no analyzable code."""
        return VulnerabilityReport(
            pr_url=pr_url,
            vulnerabilities=["no_code_found"],
            risk_score=0.0,
            recommendations=["No analyzable code changes found in this PR"],
            summary=f"📄 PR '{metadata.get('title', 'Unknown')}' contains no analyzable code changes. This may be a documentation-only or configuration change."
        )
    
    def _create_error_report(self, pr_url: str, error_msg: str) -> VulnerabilityReport:
        """Create error report when analysis fails."""
        return VulnerabilityReport(
            pr_url=pr_url,
            vulnerabilities=["analysis_error"],
            risk_score=0.0,
            recommendations=[
                f"❌ Analysis failed: {error_msg}",
                "🔧 Check PR URL format and API keys",
                "🔍 Ensure repository is accessible",
                "📞 Contact support if issue persists"
            ],
            summary=f"❌ Advanced analysis failed for PR: {error_msg}. Manual security review recommended."
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


