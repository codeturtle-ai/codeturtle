"""
Production-Ready Risk Scoring Engine
Advanced risk calculation with multiple factors and sophisticated algorithms.
"""

import logging
import math
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass
from enum import Enum

logger = logging.getLogger(__name__)

class SeverityLevel(Enum):
    """Vulnerability severity levels with numeric values."""
    CRITICAL = 4
    HIGH = 3
    MEDIUM = 2
    LOW = 1
    INFO = 0

class ConfidenceLevel(Enum):
    """Confidence levels for vulnerability detection."""
    VERY_HIGH = 0.9
    HIGH = 0.8
    MEDIUM = 0.6
    LOW = 0.4
    VERY_LOW = 0.2

@dataclass
class VulnerabilityFinding:
    """Structured vulnerability finding with metadata."""
    type: str
    severity: SeverityLevel
    confidence: float
    source: str  # 'ast', 'ai', 'kb', 'agent'
    description: str
    line_number: Optional[int] = None
    file_path: Optional[str] = None
    cwe_id: Optional[str] = None  # Common Weakness Enumeration ID

@dataclass
class PRComplexityMetrics:
    """PR complexity metrics for risk assessment."""
    total_additions: int
    total_deletions: int
    changed_files: int
    analyzable_files: int
    max_file_size: int
    avg_file_size: float
    has_config_changes: bool
    has_dependency_changes: bool
    touches_security_files: bool

class ProductionRiskCalculator:
    """
    Production-ready risk scoring engine with sophisticated algorithms.
    """
    
    def __init__(self):
        self.severity_weights = {
            SeverityLevel.CRITICAL: 1.0,
            SeverityLevel.HIGH: 0.8,
            SeverityLevel.MEDIUM: 0.5,
            SeverityLevel.LOW: 0.25,
            SeverityLevel.INFO: 0.1
        }
        
        self.source_weights = {
            'ai': 0.4,      # AI analysis gets highest weight
            'ast': 0.35,    # Static analysis is reliable
            'agent': 0.15,  # Specialized agents provide context
            'kb': 0.1       # Knowledge base provides background
        }
        
        self.vulnerability_criticality = {
            'ssti': 1.0,                    # Server-side template injection
            'sql_injection': 0.95,          # SQL injection
            'command_injection': 0.9,       # Command injection
            'insecure_deserialization': 0.85, # Unsafe deserialization
            'hardcoded_secret': 0.8,        # Hardcoded credentials
            'path_traversal': 0.75,         # Directory traversal
            'missing_auth': 0.6,            # Missing authentication
            'weak_crypto': 0.55,            # Weak cryptography
            'info_disclosure': 0.4,         # Information disclosure
            'missing_validation': 0.3       # Input validation issues
        }
    
    def calculate_risk_score(
        self,
        findings: List[VulnerabilityFinding],
        pr_metrics: PRComplexityMetrics,
        ai_confidence: float = 0.0,
        context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Calculate comprehensive risk score with detailed breakdown.
        
        Args:
            findings: List of vulnerability findings
            pr_metrics: PR complexity metrics
            ai_confidence: Overall AI analysis confidence
            context: Additional context for scoring
            
        Returns:
            Detailed risk assessment with score and breakdown
        """
        try:
            # 1. Base vulnerability score
            vuln_score = self._calculate_vulnerability_score(findings)
            
            # 2. Confidence-weighted score
            confidence_score = self._calculate_confidence_score(findings, ai_confidence)
            
            # 3. Complexity multiplier
            complexity_multiplier = self._calculate_complexity_multiplier(pr_metrics)
            
            # 4. Context adjustments
            context_adjustments = self._calculate_context_adjustments(findings, pr_metrics, context)
            
            # 5. Temporal factors (recency, frequency)
            temporal_factor = self._calculate_temporal_factor(context)
            
            # 6. Combine all factors
            base_score = (vuln_score * 0.4 + confidence_score * 0.6)
            adjusted_score = base_score * complexity_multiplier * temporal_factor
            final_score = min(adjusted_score + context_adjustments, 1.0)
            
            # 7. Generate detailed breakdown
            breakdown = self._generate_score_breakdown(
                vuln_score, confidence_score, complexity_multiplier,
                context_adjustments, temporal_factor, final_score
            )
            
            # 8. Risk categorization
            risk_category = self._categorize_risk(final_score)
            
            # 9. Recommendations based on score
            recommendations = self._generate_risk_recommendations(findings, final_score, pr_metrics)
            
            return {
                'risk_score': round(final_score, 3),
                'risk_category': risk_category,
                'confidence': self._calculate_overall_confidence(findings, ai_confidence),
                'breakdown': breakdown,
                'recommendations': recommendations,
                'findings_summary': self._summarize_findings(findings),
                'complexity_assessment': self._assess_complexity(pr_metrics),
                'metadata': {
                    'total_findings': len(findings),
                    'unique_vulnerability_types': len(set(f.type for f in findings)),
                    'highest_severity': max([f.severity.value for f in findings], default=0),
                    'calculation_method': 'production_v2.0'
                }
            }
            
        except Exception as e:
            logger.error(f"Error calculating risk score: {str(e)}")
            return self._fallback_risk_assessment(findings, ai_confidence)
    
    def _calculate_vulnerability_score(self, findings: List[VulnerabilityFinding]) -> float:
        """Calculate base vulnerability score from findings."""
        if not findings:
            return 0.0
        
        # Group findings by type
        vuln_groups = {}
        for finding in findings:
            if finding.type not in vuln_groups:
                vuln_groups[finding.type] = []
            vuln_groups[finding.type].append(finding)
        
        total_score = 0.0
        
        for vuln_type, group_findings in vuln_groups.items():
            # Get base criticality for this vulnerability type
            base_criticality = self.vulnerability_criticality.get(vuln_type, 0.5)
            
            # Calculate severity-weighted score for this group
            severity_scores = [
                self.severity_weights[f.severity] for f in group_findings
            ]
            
            # Use maximum severity but consider frequency
            max_severity = max(severity_scores)
            frequency_bonus = min(len(group_findings) * 0.1, 0.3)  # Cap at 30%
            
            group_score = base_criticality * (max_severity + frequency_bonus)
            total_score += group_score
        
        # Normalize by number of vulnerability types (diminishing returns)
        num_types = len(vuln_groups)
        if num_types > 1:
            # Multiple vulnerability types increase risk but with diminishing returns
            diversity_multiplier = 1.0 + (num_types - 1) * 0.2
            total_score *= min(diversity_multiplier, 2.0)  # Cap at 2x
        
        return min(total_score, 1.0)
    
    def _calculate_confidence_score(self, findings: List[VulnerabilityFinding], ai_confidence: float) -> float:
        """Calculate confidence-weighted score."""
        if not findings:
            return ai_confidence
        
        # Weight findings by source reliability and confidence
        weighted_scores = []
        
        for finding in findings:
            source_weight = self.source_weights.get(finding.source, 0.1)
            severity_score = self.severity_weights[finding.severity]
            confidence_weight = finding.confidence
            
            weighted_score = severity_score * confidence_weight * source_weight
            weighted_scores.append(weighted_score)
        
        # Combine with AI confidence
        findings_confidence = sum(weighted_scores) / len(weighted_scores) if weighted_scores else 0.0
        combined_confidence = (findings_confidence * 0.7 + ai_confidence * 0.3)
        
        return min(combined_confidence, 1.0)
    
    def _calculate_complexity_multiplier(self, pr_metrics: PRComplexityMetrics) -> float:
        """Calculate complexity-based risk multiplier."""
        multiplier = 1.0
        
        # Size factors
        if pr_metrics.total_additions > 500:
            multiplier += 0.3  # Very large PRs
        elif pr_metrics.total_additions > 200:
            multiplier += 0.2  # Large PRs
        elif pr_metrics.total_additions > 100:
            multiplier += 0.1  # Medium PRs
        
        # File count factors
        if pr_metrics.changed_files > 20:
            multiplier += 0.2
        elif pr_metrics.changed_files > 10:
            multiplier += 0.1
        
        # File size factors
        if pr_metrics.max_file_size > 10000:  # Very large files
            multiplier += 0.15
        elif pr_metrics.avg_file_size > 5000:  # Large average file size
            multiplier += 0.1
        
        # Special file types
        if pr_metrics.has_config_changes:
            multiplier += 0.1  # Config changes are risky
        
        if pr_metrics.has_dependency_changes:
            multiplier += 0.15  # Dependency changes introduce supply chain risk
        
        if pr_metrics.touches_security_files:
            multiplier += 0.2  # Security-related files are critical
        
        # Cap the multiplier
        return min(multiplier, 2.0)
    
    def _calculate_context_adjustments(
        self,
        findings: List[VulnerabilityFinding],
        pr_metrics: PRComplexityMetrics,
        context: Optional[Dict[str, Any]]
    ) -> float:
        """Calculate context-based score adjustments."""
        adjustments = 0.0
        
        if not context:
            return adjustments
        
        # Author reputation (if available)
        author_reputation = context.get('author_reputation', 'unknown')
        if author_reputation == 'trusted':
            adjustments -= 0.05  # Slight reduction for trusted authors
        elif author_reputation == 'new':
            adjustments += 0.1   # Increase for new contributors
        
        # Repository factors
        repo_security_score = context.get('repo_security_score', 0.5)
        if repo_security_score < 0.3:
            adjustments += 0.1  # Repos with poor security history
        elif repo_security_score > 0.8:
            adjustments -= 0.05  # Repos with good security history
        
        # Time factors
        is_urgent = context.get('is_urgent', False)
        if is_urgent:
            adjustments += 0.1  # Urgent PRs may have less review
        
        # Branch factors
        target_branch = context.get('target_branch', 'main')
        if target_branch in ['main', 'master', 'production']:
            adjustments += 0.05  # Production branches are more critical
        
        return max(min(adjustments, 0.3), -0.1)  # Cap adjustments
    
    def _calculate_temporal_factor(self, context: Optional[Dict[str, Any]]) -> float:
        """Calculate temporal risk factors."""
        if not context:
            return 1.0
        
        factor = 1.0
        
        # Recent vulnerability trends
        recent_vulns = context.get('recent_vulnerabilities', 0)
        if recent_vulns > 5:
            factor += 0.2  # High recent vulnerability activity
        elif recent_vulns > 2:
            factor += 0.1  # Moderate recent activity
        
        # Time since last security review
        days_since_review = context.get('days_since_security_review', 0)
        if days_since_review > 90:
            factor += 0.1  # Long time since last review
        
        return min(factor, 1.5)
    
    def _categorize_risk(self, score: float) -> str:
        """Categorize risk level based on score."""
        if score >= 0.9:
            return 'CRITICAL'
        elif score >= 0.7:
            return 'HIGH'
        elif score >= 0.5:
            return 'MEDIUM'
        elif score >= 0.3:
            return 'LOW'
        else:
            return 'MINIMAL'
    
    def _calculate_overall_confidence(self, findings: List[VulnerabilityFinding], ai_confidence: float) -> float:
        """Calculate overall confidence in the analysis."""
        if not findings:
            return ai_confidence
        
        # Average confidence across all findings
        finding_confidences = [f.confidence for f in findings]
        avg_finding_confidence = sum(finding_confidences) / len(finding_confidences)
        
        # Weight by source reliability
        source_weights = [self.source_weights.get(f.source, 0.1) for f in findings]
        weighted_confidence = sum(
            conf * weight for conf, weight in zip(finding_confidences, source_weights)
        ) / sum(source_weights)
        
        # Combine with AI confidence
        overall_confidence = (weighted_confidence * 0.6 + ai_confidence * 0.4)
        
        return round(overall_confidence, 3)
    
    def _generate_score_breakdown(
        self,
        vuln_score: float,
        confidence_score: float,
        complexity_multiplier: float,
        context_adjustments: float,
        temporal_factor: float,
        final_score: float
    ) -> Dict[str, Any]:
        """Generate detailed score breakdown."""
        return {
            'vulnerability_score': round(vuln_score, 3),
            'confidence_score': round(confidence_score, 3),
            'complexity_multiplier': round(complexity_multiplier, 3),
            'context_adjustments': round(context_adjustments, 3),
            'temporal_factor': round(temporal_factor, 3),
            'base_score': round((vuln_score * 0.4 + confidence_score * 0.6), 3),
            'final_score': round(final_score, 3),
            'calculation_steps': [
                f"Base vulnerability score: {vuln_score:.3f}",
                f"Confidence-weighted score: {confidence_score:.3f}",
                f"Complexity multiplier: {complexity_multiplier:.3f}",
                f"Context adjustments: {context_adjustments:+.3f}",
                f"Temporal factor: {temporal_factor:.3f}",
                f"Final score: {final_score:.3f}"
            ]
        }
    
    def _generate_risk_recommendations(
        self,
        findings: List[VulnerabilityFinding],
        risk_score: float,
        pr_metrics: PRComplexityMetrics
    ) -> List[str]:
        """Generate risk-based recommendations."""
        recommendations = []
        
        # Score-based recommendations
        if risk_score >= 0.9:
            recommendations.append("🚨 CRITICAL: Block deployment until vulnerabilities are fixed")
            recommendations.append("Require security team review before merging")
        elif risk_score >= 0.7:
            recommendations.append("⚠️ HIGH RISK: Require senior developer review")
            recommendations.append("Consider additional security testing")
        elif risk_score >= 0.5:
            recommendations.append("📋 MEDIUM RISK: Standard security review recommended")
        
        # Vulnerability-specific recommendations
        vuln_types = set(f.type for f in findings)
        if 'ssti' in vuln_types:
            recommendations.append("🔥 SSTI detected: Immediate remediation required")
        if 'sql_injection' in vuln_types:
            recommendations.append("💉 SQL injection risk: Use parameterized queries")
        if 'hardcoded_secret' in vuln_types:
            recommendations.append("🔑 Hardcoded secrets: Move to environment variables")
        
        # Complexity-based recommendations
        if pr_metrics.total_additions > 500:
            recommendations.append("📏 Large PR: Consider breaking into smaller changes")
        if pr_metrics.changed_files > 15:
            recommendations.append("📁 Many files changed: Extra review attention needed")
        
        return recommendations[:6]  # Limit to 6 most important
    
    def _summarize_findings(self, findings: List[VulnerabilityFinding]) -> Dict[str, Any]:
        """Summarize findings for reporting."""
        if not findings:
            return {'total': 0, 'by_severity': {}, 'by_type': {}}
        
        by_severity = {}
        by_type = {}
        
        for finding in findings:
            # Count by severity
            severity_name = finding.severity.name
            by_severity[severity_name] = by_severity.get(severity_name, 0) + 1
            
            # Count by type
            by_type[finding.type] = by_type.get(finding.type, 0) + 1
        
        return {
            'total': len(findings),
            'by_severity': by_severity,
            'by_type': by_type,
            'highest_severity': max([f.severity.name for f in findings], default='INFO'),
            'most_common_type': max(by_type.items(), key=lambda x: x[1])[0] if by_type else None
        }
    
    def _assess_complexity(self, pr_metrics: PRComplexityMetrics) -> Dict[str, Any]:
        """Assess PR complexity."""
        complexity_score = 0
        
        # Size complexity
        if pr_metrics.total_additions > 1000:
            complexity_score += 3
        elif pr_metrics.total_additions > 500:
            complexity_score += 2
        elif pr_metrics.total_additions > 100:
            complexity_score += 1
        
        # File complexity
        if pr_metrics.changed_files > 20:
            complexity_score += 2
        elif pr_metrics.changed_files > 10:
            complexity_score += 1
        
        # Special factors
        if pr_metrics.has_dependency_changes:
            complexity_score += 2
        if pr_metrics.touches_security_files:
            complexity_score += 1
        
        complexity_levels = {
            0: 'MINIMAL',
            1: 'LOW',
            2: 'LOW',
            3: 'MEDIUM',
            4: 'MEDIUM',
            5: 'HIGH',
            6: 'HIGH',
            7: 'VERY_HIGH',
            8: 'VERY_HIGH'
        }
        
        level = complexity_levels.get(min(complexity_score, 8), 'VERY_HIGH')
        
        return {
            'level': level,
            'score': complexity_score,
            'factors': {
                'size': pr_metrics.total_additions,
                'files': pr_metrics.changed_files,
                'has_dependencies': pr_metrics.has_dependency_changes,
                'touches_security': pr_metrics.touches_security_files
            }
        }
    
    def _fallback_risk_assessment(self, findings: List[VulnerabilityFinding], ai_confidence: float) -> Dict[str, Any]:
        """Fallback risk assessment when main calculation fails."""
        logger.warning("Using fallback risk assessment")
        
        if not findings:
            return {
                'risk_score': ai_confidence * 0.5,
                'risk_category': 'LOW',
                'confidence': ai_confidence,
                'breakdown': {'error': 'Fallback calculation used'},
                'recommendations': ['Manual review recommended due to calculation error'],
                'findings_summary': {'total': 0},
                'complexity_assessment': {'level': 'UNKNOWN'},
                'metadata': {'calculation_method': 'fallback'}
            }
        
        # Simple fallback calculation
        max_severity = max([self.severity_weights[f.severity] for f in findings])
        avg_confidence = sum([f.confidence for f in findings]) / len(findings)
        simple_score = (max_severity + avg_confidence) / 2
        
        return {
            'risk_score': round(simple_score, 3),
            'risk_category': self._categorize_risk(simple_score),
            'confidence': avg_confidence,
            'breakdown': {'error': 'Simplified fallback calculation'},
            'recommendations': ['Manual review recommended', 'Calculation error occurred'],
            'findings_summary': {'total': len(findings)},
            'complexity_assessment': {'level': 'UNKNOWN'},
            'metadata': {'calculation_method': 'fallback'}
        }