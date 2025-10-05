"""Production-grade risk scoring engine for vulnerability assessment."""

import logging
from typing import List, Dict, Any

logger = logging.getLogger(__name__)


class RiskScorer:
    """Advanced risk scoring with severity weighting and confidence adjustment."""

    # Severity weights based on industry standards (CVSS-like)
    SEVERITY_WEIGHTS = {
        "critical": 1.0,
        "high": 0.7,
        "medium": 0.4,
        "low": 0.1,
    }

    # Vulnerability type weights (some are more dangerous than others)
    VULNERABILITY_WEIGHTS = {
        "code_execution": 1.0,
        "sql_injection": 0.95,
        "command_injection": 0.95,
        "insecure_deserialization": 0.9,
        "hardcoded_secret": 0.85,
        "hardcoded_password": 0.9,
        "hardcoded_api_key": 0.85,
        "hardcoded_token": 0.85,
        "missing_authentication": 0.75,
        "weak_cryptography": 0.5,
        "dangerous_import": 0.3,
        "potential_sql_injection": 0.6,
        "syntax_error": 0.1,
    }

    def __init__(self):
        pass

    def calculate_risk_score(
        self,
        findings: List[Dict[str, Any]],
        ai_confidence: float = 0.0,
        kb_matches: int = 0,
    ) -> Dict[str, Any]:
        """
        Calculate comprehensive risk score using multiple factors.
        
        Args:
            findings: List of AST/static analysis findings
            ai_confidence: AI model confidence score (0-1)
            kb_matches: Number of knowledge base matches
            
        Returns:
            Dict with risk_score, breakdown, and severity_distribution
        """
        if not findings and ai_confidence == 0.0:
            return {
                "risk_score": 0.0,
                "severity_distribution": {"critical": 0, "high": 0, "medium": 0, "low": 0},
                "confidence": 0.0,
                "total_findings": 0,
                "weighted_score": 0.0,
            }

        # Calculate weighted scores for each finding
        weighted_scores = []
        severity_counts = {"critical": 0, "high": 0, "medium": 0, "low": 0}

        for finding in findings:
            severity = finding.get("severity", "medium").lower()
            confidence = finding.get("confidence", 0.5)
            vuln_type = finding.get("vulnerability", "unknown")

            # Get weights
            severity_weight = self.SEVERITY_WEIGHTS.get(severity, 0.5)
            vuln_weight = self.VULNERABILITY_WEIGHTS.get(vuln_type, 0.5)

            # Calculate weighted score for this finding
            finding_score = severity_weight * confidence * vuln_weight

            weighted_scores.append(finding_score)
            severity_counts[severity] = severity_counts.get(severity, 0) + 1

        # Base score from static analysis
        if weighted_scores:
            static_score = sum(weighted_scores) / len(weighted_scores)
        else:
            static_score = 0.0

        # Factor in AI confidence (if available)
        if ai_confidence > 0:
            # AI confidence boosts or reduces the score
            ai_factor = 0.3  # AI contributes 30% max
            combined_score = (static_score * 0.7) + (ai_confidence * ai_factor)
        else:
            combined_score = static_score

        # Factor in knowledge base matches (indicates known vulnerabilities)
        if kb_matches > 0:
            # Each KB match adds a small boost (indicates pattern recognition)
            kb_boost = min(kb_matches * 0.05, 0.15)  # Max 15% boost
            combined_score = min(combined_score + kb_boost, 1.0)

        # Normalize to 0-1 range
        final_score = max(0.0, min(combined_score, 1.0))

        return {
            "risk_score": round(final_score, 3),
            "severity_distribution": severity_counts,
            "confidence": round(self._calculate_overall_confidence(findings, ai_confidence), 3),
            "total_findings": len(findings),
            "weighted_score": round(static_score, 3),
            "ai_contribution": round(ai_confidence * 0.3 if ai_confidence > 0 else 0.0, 3),
            "kb_boost": round(min(kb_matches * 0.05, 0.15) if kb_matches > 0 else 0.0, 3),
        }

    def _calculate_overall_confidence(self, findings: List[Dict[str, Any]], ai_confidence: float) -> float:
        """Calculate overall confidence in the analysis."""
        if not findings:
            return ai_confidence

        # Average confidence from static findings
        static_confidences = [f.get("confidence", 0.5) for f in findings]
        avg_static = sum(static_confidences) / len(static_confidences) if static_confidences else 0.0

        # Combine with AI confidence if available
        if ai_confidence > 0:
            return (avg_static * 0.6) + (ai_confidence * 0.4)
        else:
            return avg_static

    def get_risk_level(self, risk_score: float) -> str:
        """Convert numeric risk score to categorical level."""
        if risk_score >= 0.8:
            return "CRITICAL"
        elif risk_score >= 0.6:
            return "HIGH"
        elif risk_score >= 0.4:
            return "MEDIUM"
        elif risk_score > 0.0:
            return "LOW"
        else:
            return "NONE"

    def get_recommendations(self, findings: List[Dict[str, Any]], risk_score: float) -> List[str]:
        """Generate prioritized recommendations based on findings."""
        recommendations = []
        vuln_types_seen = set()

        # Sort findings by severity and confidence
        sorted_findings = sorted(
            findings,
            key=lambda x: (
                self.SEVERITY_WEIGHTS.get(x.get("severity", "medium"), 0.5),
                x.get("confidence", 0.5),
            ),
            reverse=True,
        )

        # Add specific recommendations for each unique vulnerability type
        for finding in sorted_findings:
            vuln_type = finding.get("vulnerability")
            if vuln_type and vuln_type not in vuln_types_seen:
                vuln_types_seen.add(vuln_type)

                # Get remediation if available
                if "remediation" in finding:
                    recommendations.append(finding["remediation"])
                else:
                    # Default recommendations by type
                    default_recs = self._get_default_recommendation(vuln_type)
                    if default_recs:
                        recommendations.append(default_recs)

        # Add general recommendations based on risk level
        if risk_score >= 0.8:
            recommendations.insert(0, "URGENT: Address critical vulnerabilities immediately")
        elif risk_score >= 0.6:
            recommendations.insert(0, "HIGH PRIORITY: Review and fix identified issues")

        # Deduplicate while preserving order
        seen = set()
        unique_recs = []
        for rec in recommendations:
            if rec not in seen:
                seen.add(rec)
                unique_recs.append(rec)

        return unique_recs[:10]  # Limit to top 10

    def _get_default_recommendation(self, vuln_type: str) -> str:
        """Get default recommendation for vulnerability type."""
        recommendations_map = {
            "code_execution": "Remove eval/exec calls and use safer alternatives",
            "sql_injection": "Use parameterized queries or ORM instead of string concatenation",
            "command_injection": "Use subprocess with shell=False and validate input",
            "hardcoded_secret": "Move secrets to environment variables or secret management service",
            "hardcoded_password": "Never hardcode passwords; use environment variables",
            "hardcoded_api_key": "Store API keys in secure vaults or environment variables",
            "missing_authentication": "Add authentication middleware to protect endpoints",
            "weak_cryptography": "Use SHA-256 or stronger cryptographic algorithms",
            "insecure_deserialization": "Validate and sanitize input before deserialization",
        }
        return recommendations_map.get(vuln_type, "Review code for security best practices")

