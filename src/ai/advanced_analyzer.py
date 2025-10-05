"""
Advanced AI Analysis Engine
Complete AI-powered vulnerability analysis with sophisticated prompting and response handling.
"""

import logging
import json
import re
import asyncio
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass
from enum import Enum
import hashlib

logger = logging.getLogger(__name__)

class AnalysisMode(Enum):
    """Analysis modes for different use cases."""
    COMPREHENSIVE = "comprehensive"  # Full analysis with all vulnerability types
    FOCUSED = "focused"              # Focus on specific vulnerability types
    QUICK = "quick"                  # Fast analysis for CI/CD
    DEEP = "deep"                    # Thorough analysis for security review

class VulnerabilityCategory(Enum):
    """Vulnerability categories for focused analysis."""
    INJECTION = "injection"          # SQL, NoSQL, Command, LDAP injection
    BROKEN_AUTH = "broken_auth"      # Authentication and session management
    SENSITIVE_DATA = "sensitive_data" # Sensitive data exposure
    XXE = "xxe"                      # XML External Entities
    BROKEN_ACCESS = "broken_access"  # Broken access control
    SECURITY_MISCONFIG = "security_misconfig"  # Security misconfiguration
    XSS = "xss"                      # Cross-Site Scripting
    INSECURE_DESERIAL = "insecure_deserial"  # Insecure deserialization
    KNOWN_VULNS = "known_vulns"      # Using components with known vulnerabilities
    INSUFFICIENT_LOG = "insufficient_log"  # Insufficient logging and monitoring

@dataclass
class AnalysisContext:
    """Context for AI analysis."""
    code_snippet: str
    file_path: Optional[str] = None
    pr_title: Optional[str] = None
    pr_description: Optional[str] = None
    author: Optional[str] = None
    target_branch: Optional[str] = None
    framework_info: Optional[Dict[str, Any]] = None
    previous_findings: Optional[List[Dict[str, Any]]] = None

@dataclass
class AIAnalysisResult:
    """Structured AI analysis result."""
    vulnerabilities: List[Dict[str, Any]]
    confidence: float
    severity_assessment: str
    recommendations: List[str]
    explanation: str
    false_positive_likelihood: float
    suggested_fixes: List[Dict[str, Any]]
    compliance_issues: List[str]
    performance_impact: Optional[str]
    metadata: Dict[str, Any]

class AdvancedAIAnalyzer:
    """
    Advanced AI analyzer with sophisticated prompting and response handling.
    """
    
    def __init__(self, ai_client, model: str = "gpt-3.5-turbo"):
        self.ai_client = ai_client
        self.model = model
        self.analysis_cache = {}  # Simple in-memory cache
        
        # Vulnerability type mappings
        self.vulnerability_mappings = {
            'sql_injection': {
                'category': VulnerabilityCategory.INJECTION,
                'cwe': 'CWE-89',
                'owasp': 'A03:2021 – Injection',
                'severity_base': 'HIGH'
            },
            'ssti': {
                'category': VulnerabilityCategory.INJECTION,
                'cwe': 'CWE-94',
                'owasp': 'A03:2021 – Injection',
                'severity_base': 'CRITICAL'
            },
            'hardcoded_secret': {
                'category': VulnerabilityCategory.SENSITIVE_DATA,
                'cwe': 'CWE-798',
                'owasp': 'A02:2021 – Cryptographic Failures',
                'severity_base': 'HIGH'
            },
            'missing_auth': {
                'category': VulnerabilityCategory.BROKEN_AUTH,
                'cwe': 'CWE-306',
                'owasp': 'A07:2021 – Identification and Authentication Failures',
                'severity_base': 'MEDIUM'
            },
            'command_injection': {
                'category': VulnerabilityCategory.INJECTION,
                'cwe': 'CWE-78',
                'owasp': 'A03:2021 – Injection',
                'severity_base': 'HIGH'
            },
            'insecure_deserialization': {
                'category': VulnerabilityCategory.INSECURE_DESERIAL,
                'cwe': 'CWE-502',
                'owasp': 'A08:2021 – Software and Data Integrity Failures',
                'severity_base': 'HIGH'
            }
        }
    
    async def analyze_code(
        self,
        context: AnalysisContext,
        mode: AnalysisMode = AnalysisMode.COMPREHENSIVE,
        focus_categories: Optional[List[VulnerabilityCategory]] = None
    ) -> AIAnalysisResult:
        """
        Perform advanced AI analysis on code.
        
        Args:
            context: Analysis context with code and metadata
            mode: Analysis mode (comprehensive, focused, quick, deep)
            focus_categories: Specific vulnerability categories to focus on
            
        Returns:
            Structured AI analysis result
        """
        try:
            # Check cache first
            cache_key = self._generate_cache_key(context, mode, focus_categories)
            if cache_key in self.analysis_cache:
                logger.info("Returning cached analysis result")
                return self.analysis_cache[cache_key]
            
            # Generate appropriate prompt based on mode
            prompt = self._generate_analysis_prompt(context, mode, focus_categories)
            
            # Call AI with retry logic
            ai_response = await self._call_ai_with_retry(prompt, mode)
            
            # Parse and structure the response
            structured_result = self._parse_ai_response(ai_response, context)
            
            # Enhance with additional analysis
            enhanced_result = await self._enhance_analysis_result(structured_result, context)
            
            # Cache the result
            self.analysis_cache[cache_key] = enhanced_result
            
            return enhanced_result
            
        except Exception as e:
            logger.error(f"Error in AI analysis: {str(e)}")
            return self._create_fallback_result(context, str(e))
    
    def _generate_analysis_prompt(
        self,
        context: AnalysisContext,
        mode: AnalysisMode,
        focus_categories: Optional[List[VulnerabilityCategory]]
    ) -> str:
        """Generate sophisticated analysis prompt based on mode and context."""
        
        base_system_prompt = """You are an expert cybersecurity analyst specializing in application security and vulnerability assessment. You have deep knowledge of:

- OWASP Top 10 vulnerabilities
- Common Weakness Enumeration (CWE)
- Secure coding practices
- FastAPI and Python security patterns
- Static and dynamic analysis techniques

Your analysis should be thorough, accurate, and actionable."""

        if mode == AnalysisMode.COMPREHENSIVE:
            return self._generate_comprehensive_prompt(context, base_system_prompt)
        elif mode == AnalysisMode.FOCUSED:
            return self._generate_focused_prompt(context, base_system_prompt, focus_categories)
        elif mode == AnalysisMode.QUICK:
            return self._generate_quick_prompt(context, base_system_prompt)
        elif mode == AnalysisMode.DEEP:
            return self._generate_deep_prompt(context, base_system_prompt)
        else:
            return self._generate_comprehensive_prompt(context, base_system_prompt)
    
    def _generate_comprehensive_prompt(self, context: AnalysisContext, system_prompt: str) -> str:
        """Generate comprehensive analysis prompt."""
        
        vulnerability_focus = """
Analyze for these vulnerability categories:

1. **Injection Vulnerabilities**:
   - SQL Injection (CWE-89): Raw queries, string concatenation, ORM misuse
   - NoSQL Injection (CWE-943): MongoDB, Redis, Elasticsearch injection
   - Command Injection (CWE-78): subprocess, os.system, shell commands
   - LDAP Injection (CWE-90): LDAP query manipulation
   - Server-Side Template Injection (CWE-94): eval, exec, unsafe templating

2. **Authentication & Authorization**:
   - Missing Authentication (CWE-306): Unprotected endpoints
   - Weak Authentication (CWE-287): Poor password policies, weak tokens
   - Session Management (CWE-384): Session fixation, weak session handling
   - Privilege Escalation (CWE-269): Improper access controls

3. **Sensitive Data Exposure**:
   - Hardcoded Secrets (CWE-798): API keys, passwords, tokens in code
   - Information Disclosure (CWE-200): Error messages, debug info
   - Weak Cryptography (CWE-327): Weak algorithms, poor key management
   - Data Leakage (CWE-532): Logs, responses, headers

4. **Input Validation & Output Encoding**:
   - Cross-Site Scripting (CWE-79): Reflected, stored, DOM-based XSS
   - Path Traversal (CWE-22): Directory traversal, file inclusion
   - XML External Entity (CWE-611): XXE attacks
   - Deserialization (CWE-502): Unsafe pickle, yaml.load

5. **Security Misconfiguration**:
   - Debug Mode (CWE-489): Debug enabled in production
   - CORS Misconfiguration (CWE-942): Overly permissive CORS
   - HTTP Security Headers: Missing security headers
   - Default Configurations: Unchanged default settings

6. **Business Logic & Race Conditions**:
   - Race Conditions (CWE-362): TOCTOU, concurrent access
   - Business Logic Flaws: Workflow bypasses, logic errors
   - Resource Management (CWE-400): DoS, resource exhaustion
"""

        code_context = f"""
**Code Analysis Context:**
- File: {context.file_path or 'Unknown'}
- PR Title: {context.pr_title or 'Not provided'}
- Author: {context.author or 'Unknown'}
- Target Branch: {context.target_branch or 'Unknown'}
- Framework: FastAPI/Python

**Code to Analyze:**
```python
{context.code_snippet}
```
"""

        response_format = """
**Required Response Format (JSON):**
```json
{
  "vulnerabilities": [
    {
      "type": "vulnerability_type",
      "severity": "CRITICAL|HIGH|MEDIUM|LOW|INFO",
      "confidence": 0.0-1.0,
      "cwe_id": "CWE-XXX",
      "owasp_category": "OWASP category",
      "description": "Detailed description of the vulnerability",
      "location": "File path and line number if applicable",
      "impact": "Potential impact of exploitation",
      "likelihood": "Likelihood of exploitation",
      "evidence": "Code evidence supporting the finding"
    }
  ],
  "overall_confidence": 0.0-1.0,
  "severity_assessment": "Overall severity assessment",
  "false_positive_likelihood": 0.0-1.0,
  "recommendations": [
    "Specific, actionable recommendations"
  ],
  "suggested_fixes": [
    {
      "vulnerability": "vulnerability_type",
      "fix_description": "How to fix this issue",
      "code_example": "Secure code example",
      "priority": "HIGH|MEDIUM|LOW"
    }
  ],
  "compliance_issues": [
    "OWASP, CWE, or other compliance issues"
  ],
  "explanation": "Detailed explanation of the analysis",
  "performance_impact": "Any performance implications of the vulnerabilities or fixes"
}
```
"""

        return f"{system_prompt}\n\n{vulnerability_focus}\n\n{code_context}\n\n{response_format}"
    
    def _generate_focused_prompt(
        self,
        context: AnalysisContext,
        system_prompt: str,
        focus_categories: Optional[List[VulnerabilityCategory]]
    ) -> str:
        """Generate focused analysis prompt for specific vulnerability categories."""
        
        if not focus_categories:
            focus_categories = [VulnerabilityCategory.INJECTION, VulnerabilityCategory.SENSITIVE_DATA]
        
        category_descriptions = {
            VulnerabilityCategory.INJECTION: "Focus on injection vulnerabilities: SQL, NoSQL, Command, LDAP, Template injection",
            VulnerabilityCategory.BROKEN_AUTH: "Focus on authentication and authorization issues",
            VulnerabilityCategory.SENSITIVE_DATA: "Focus on sensitive data exposure and cryptographic issues",
            VulnerabilityCategory.BROKEN_ACCESS: "Focus on access control and privilege escalation",
            VulnerabilityCategory.SECURITY_MISCONFIG: "Focus on security misconfigurations",
            VulnerabilityCategory.INSECURE_DESERIAL: "Focus on insecure deserialization vulnerabilities"
        }
        
        focus_description = "\n".join([
            f"- {category_descriptions.get(cat, cat.value)}"
            for cat in focus_categories
        ])
        
        return f"""{system_prompt}

**FOCUSED ANALYSIS REQUEST**

Focus your analysis specifically on these vulnerability categories:
{focus_description}

**Code to Analyze:**
```python
{context.code_snippet}
```

**Context:**
- File: {context.file_path or 'Unknown'}
- PR Title: {context.pr_title or 'Not provided'}

Provide a focused analysis in JSON format with high confidence findings for the specified categories only.
"""
    
    def _generate_quick_prompt(self, context: AnalysisContext, system_prompt: str) -> str:
        """Generate quick analysis prompt for CI/CD integration."""
        
        return f"""{system_prompt}

**QUICK SECURITY SCAN**

Perform a rapid security analysis focusing on the most critical vulnerabilities:
- SQL Injection
- Command Injection  
- Server-Side Template Injection (eval/exec)
- Hardcoded Secrets
- Missing Authentication

**Code:**
```python
{context.code_snippet}
```

Return a concise JSON response with only high-confidence, critical findings:
{{
  "critical_vulnerabilities": ["list of critical issues"],
  "confidence": 0.0-1.0,
  "immediate_actions": ["urgent actions needed"],
  "safe_to_deploy": true/false
}}
"""
    
    def _generate_deep_prompt(self, context: AnalysisContext, system_prompt: str) -> str:
        """Generate deep analysis prompt for thorough security review."""
        
        return f"""{system_prompt}

**DEEP SECURITY ANALYSIS**

Perform an exhaustive security analysis including:

1. **Static Analysis**: Code patterns, data flow, control flow
2. **Dynamic Behavior**: Runtime implications, state changes
3. **Architecture Review**: Design patterns, security architecture
4. **Threat Modeling**: Attack vectors, threat scenarios
5. **Compliance**: OWASP, CWE, regulatory requirements
6. **Business Logic**: Workflow security, business rule validation

**Extended Context:**
- File: {context.file_path or 'Unknown'}
- PR Title: {context.pr_title or 'Not provided'}
- PR Description: {context.pr_description or 'Not provided'}
- Author: {context.author or 'Unknown'}
- Target Branch: {context.target_branch or 'Unknown'}

**Code for Deep Analysis:**
```python
{context.code_snippet}
```

**Previous Findings (if any):**
{json.dumps(context.previous_findings, indent=2) if context.previous_findings else 'None'}

Provide a comprehensive analysis with:
- Detailed vulnerability assessment
- Attack scenario modeling
- Risk quantification
- Comprehensive remediation plan
- Long-term security recommendations
"""
    
    async def _call_ai_with_retry(self, prompt: str, mode: AnalysisMode) -> str:
        """Call AI with retry logic and mode-specific parameters."""
        
        # Adjust parameters based on mode
        if mode == AnalysisMode.QUICK:
            max_tokens = 500
            temperature = 0.1
        elif mode == AnalysisMode.DEEP:
            max_tokens = 2000
            temperature = 0.05
        else:
            max_tokens = 1000
            temperature = 0.1
        
        payload = {
            "model": self.model,
            "messages": [
                {
                    "role": "system",
                    "content": "You are an expert cybersecurity analyst. Provide accurate, actionable security analysis."
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            "max_tokens": max_tokens,
            "temperature": temperature,
            "top_p": 0.9
        }
        
        max_retries = 3
        for attempt in range(max_retries):
            try:
                result = await self.ai_client._make_request("/completions", payload)
                
                if "choices" in result and len(result["choices"]) > 0:
                    response_text = result["choices"][0].get("message", {}).get("content", "")
                    if response_text.strip():
                        return response_text
                
                raise ValueError("Empty or invalid AI response")
                
            except Exception as e:
                logger.warning(f"AI call attempt {attempt + 1} failed: {str(e)}")
                if attempt == max_retries - 1:
                    raise
                await asyncio.sleep(2 ** attempt)  # Exponential backoff
        
        raise Exception("All AI call attempts failed")
    
    def _parse_ai_response(self, response_text: str, context: AnalysisContext) -> AIAnalysisResult:
        """Parse AI response into structured result."""
        
        try:
            # Try to extract JSON from response
            json_match = re.search(r'\{.*\}', response_text, re.DOTALL)
            if json_match:
                json_str = json_match.group()
                parsed_data = json.loads(json_str)
                
                return AIAnalysisResult(
                    vulnerabilities=parsed_data.get("vulnerabilities", []),
                    confidence=float(parsed_data.get("overall_confidence", 0.5)),
                    severity_assessment=parsed_data.get("severity_assessment", "UNKNOWN"),
                    recommendations=parsed_data.get("recommendations", []),
                    explanation=parsed_data.get("explanation", ""),
                    false_positive_likelihood=float(parsed_data.get("false_positive_likelihood", 0.3)),
                    suggested_fixes=parsed_data.get("suggested_fixes", []),
                    compliance_issues=parsed_data.get("compliance_issues", []),
                    performance_impact=parsed_data.get("performance_impact"),
                    metadata={
                        "raw_response": response_text[:500],
                        "parsing_method": "json_extraction",
                        "response_length": len(response_text)
                    }
                )
            
            # Fallback to natural language parsing
            return self._parse_natural_language_response(response_text, context)
            
        except Exception as e:
            logger.error(f"Error parsing AI response: {str(e)}")
            return self._create_parsing_fallback_result(response_text, context)
    
    def _parse_natural_language_response(self, response_text: str, context: AnalysisContext) -> AIAnalysisResult:
        """Parse natural language AI response."""
        
        vulnerabilities = []
        recommendations = []
        
        # Extract vulnerability mentions
        vuln_patterns = {
            'sql_injection': ['sql injection', 'sql query', 'database injection'],
            'ssti': ['template injection', 'eval', 'exec', 'code execution'],
            'hardcoded_secret': ['hardcoded', 'secret', 'password', 'api key'],
            'command_injection': ['command injection', 'subprocess', 'shell'],
            'missing_auth': ['authentication', 'authorization', 'access control'],
            'insecure_deserialization': ['deserialization', 'pickle', 'yaml.load']
        }
        
        response_lower = response_text.lower()
        
        for vuln_type, patterns in vuln_patterns.items():
            if any(pattern in response_lower for pattern in patterns):
                # Estimate confidence based on pattern strength
                confidence = 0.7 if any(p in response_lower for p in patterns[:2]) else 0.5
                
                vulnerabilities.append({
                    "type": vuln_type,
                    "severity": self.vulnerability_mappings.get(vuln_type, {}).get("severity_base", "MEDIUM"),
                    "confidence": confidence,
                    "description": f"Potential {vuln_type.replace('_', ' ')} detected in code analysis",
                    "evidence": "Natural language analysis"
                })
        
        # Extract recommendations
        rec_indicators = ['recommend', 'should', 'fix', 'improve', 'secure']
        lines = response_text.split('\n')
        for line in lines:
            if any(indicator in line.lower() for indicator in rec_indicators):
                if len(line.strip()) > 10:  # Avoid very short lines
                    recommendations.append(line.strip())
        
        return AIAnalysisResult(
            vulnerabilities=vulnerabilities,
            confidence=0.6,  # Lower confidence for natural language parsing
            severity_assessment="MEDIUM",
            recommendations=recommendations[:5],  # Limit recommendations
            explanation=response_text[:500],
            false_positive_likelihood=0.4,
            suggested_fixes=[],
            compliance_issues=[],
            performance_impact=None,
            metadata={
                "parsing_method": "natural_language",
                "response_length": len(response_text)
            }
        )
    
    async def _enhance_analysis_result(self, result: AIAnalysisResult, context: AnalysisContext) -> AIAnalysisResult:
        """Enhance analysis result with additional processing."""
        
        # Enhance vulnerabilities with additional metadata
        enhanced_vulns = []
        for vuln in result.vulnerabilities:
            enhanced_vuln = vuln.copy()
            
            vuln_type = vuln.get("type", "unknown")
            if vuln_type in self.vulnerability_mappings:
                mapping = self.vulnerability_mappings[vuln_type]
                enhanced_vuln.update({
                    "cwe_id": mapping["cwe"],
                    "owasp_category": mapping["owasp"],
                    "category": mapping["category"].value
                })
            
            # Add risk scoring
            enhanced_vuln["risk_score"] = self._calculate_vulnerability_risk(enhanced_vuln)
            
            enhanced_vulns.append(enhanced_vuln)
        
        # Sort vulnerabilities by risk score
        enhanced_vulns.sort(key=lambda x: x.get("risk_score", 0), reverse=True)
        
        # Enhance recommendations with prioritization
        prioritized_recommendations = self._prioritize_recommendations(
            result.recommendations, enhanced_vulns
        )
        
        # Update result
        result.vulnerabilities = enhanced_vulns
        result.recommendations = prioritized_recommendations
        result.metadata.update({
            "enhancement_applied": True,
            "vulnerability_count": len(enhanced_vulns),
            "high_risk_count": len([v for v in enhanced_vulns if v.get("risk_score", 0) > 0.7])
        })
        
        return result
    
    def _calculate_vulnerability_risk(self, vulnerability: Dict[str, Any]) -> float:
        """Calculate risk score for individual vulnerability."""
        
        severity_scores = {
            "CRITICAL": 1.0,
            "HIGH": 0.8,
            "MEDIUM": 0.5,
            "LOW": 0.25,
            "INFO": 0.1
        }
        
        severity = vulnerability.get("severity", "MEDIUM")
        confidence = float(vulnerability.get("confidence", 0.5))
        
        base_score = severity_scores.get(severity, 0.5)
        risk_score = base_score * confidence
        
        # Adjust based on vulnerability type
        vuln_type = vulnerability.get("type", "")
        if vuln_type in ["ssti", "sql_injection", "command_injection"]:
            risk_score *= 1.2  # Boost for high-impact vulnerabilities
        
        return min(risk_score, 1.0)
    
    def _prioritize_recommendations(self, recommendations: List[str], vulnerabilities: List[Dict[str, Any]]) -> List[str]:
        """Prioritize recommendations based on vulnerability severity."""
        
        # Create priority mapping
        priority_keywords = {
            "critical": 3,
            "immediate": 3,
            "urgent": 3,
            "fix": 2,
            "secure": 2,
            "improve": 1,
            "consider": 1
        }
        
        scored_recommendations = []
        for rec in recommendations:
            score = 0
            rec_lower = rec.lower()
            
            # Score based on keywords
            for keyword, points in priority_keywords.items():
                if keyword in rec_lower:
                    score += points
            
            # Boost score if related to high-risk vulnerabilities
            for vuln in vulnerabilities:
                if vuln.get("risk_score", 0) > 0.7:
                    vuln_type = vuln.get("type", "").replace("_", " ")
                    if vuln_type in rec_lower:
                        score += 2
            
            scored_recommendations.append((score, rec))
        
        # Sort by score and return recommendations
        scored_recommendations.sort(key=lambda x: x[0], reverse=True)
        return [rec for score, rec in scored_recommendations]
    
    def _generate_cache_key(
        self,
        context: AnalysisContext,
        mode: AnalysisMode,
        focus_categories: Optional[List[VulnerabilityCategory]]
    ) -> str:
        """Generate cache key for analysis result."""
        
        # Create hash of code content
        code_hash = hashlib.md5(context.code_snippet.encode()).hexdigest()
        
        # Include mode and categories in key
        categories_str = ",".join([cat.value for cat in focus_categories]) if focus_categories else ""
        
        cache_key = f"{code_hash}_{mode.value}_{categories_str}"
        return cache_key
    
    def _create_fallback_result(self, context: AnalysisContext, error_msg: str) -> AIAnalysisResult:
        """Create fallback result when AI analysis fails."""
        
        return AIAnalysisResult(
            vulnerabilities=[{
                "type": "analysis_error",
                "severity": "INFO",
                "confidence": 0.0,
                "description": f"AI analysis failed: {error_msg}",
                "evidence": "Error occurred during analysis"
            }],
            confidence=0.0,
            severity_assessment="UNKNOWN",
            recommendations=["Manual code review recommended due to analysis error"],
            explanation=f"Analysis failed with error: {error_msg}",
            false_positive_likelihood=1.0,
            suggested_fixes=[],
            compliance_issues=[],
            performance_impact=None,
            metadata={
                "error": error_msg,
                "fallback_used": True
            }
        )
    
    def _create_parsing_fallback_result(self, response_text: str, context: AnalysisContext) -> AIAnalysisResult:
        """Create fallback result when response parsing fails."""
        
        return AIAnalysisResult(
            vulnerabilities=[],
            confidence=0.3,
            severity_assessment="UNKNOWN",
            recommendations=["Unable to parse AI response - manual review recommended"],
            explanation="AI response could not be parsed into structured format",
            false_positive_likelihood=0.5,
            suggested_fixes=[],
            compliance_issues=[],
            performance_impact=None,
            metadata={
                "parsing_error": True,
                "raw_response": response_text[:200]
            }
        )