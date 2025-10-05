from __future__ import annotations
import logging
import re
from typing import Dict, Any, List

logger = logging.getLogger(__name__)

class MultiAgentRouter:
    """Routes vulnerability analysis to specialized sub-agents based on type."""

    def __init__(self, base_agent) -> None:
        self.base_agent = base_agent
        self.specialized_agents = {
            "sql_injection": self._sql_agent,
            "ssti": self._ssti_agent,
            "hardcoded_secret": self._secret_agent,
            "missing_auth": self._auth_agent,
            "command_injection": self._command_injection_agent,
            "insecure_deserialization": self._deserialization_agent,
        }

    async def route_analysis(self, code: str, detected_vulns: List[str]) -> Dict[str, Any]:
        """Route to specialized agents based on detected vulnerabilities."""
        results = {}
        for vuln in detected_vulns:
            agent_func = self.specialized_agents.get(vuln, self._default_agent)
            try:
                specialized_result = await agent_func(code, vuln)
                results[vuln] = specialized_result
            except Exception as e:
                logger.error(f"Error in specialized agent for {vuln}: {e}")
                results[vuln] = {"error": str(e), "vulnerability": vuln}
        return results

    async def _sql_agent(self, code: str, vuln: str) -> Dict[str, Any]:
        """Specialized SQL injection analysis."""
        findings = []
        confidence = 0.0
        
        # Look for SQL injection patterns
        sql_patterns = [
            (r'execute\s*\([^)]*\+[^)]*\)', 0.9, "String concatenation in SQL execute"),
            (r'f["\'].*SELECT.*{.*}["\']', 0.8, "f-string in SQL query"),
            (r'".*SELECT.*".*%', 0.7, "String formatting in SQL"),
            (r'\.format\s*\(.*SELECT', 0.7, "String format in SQL query"),
        ]
        
        for pattern, conf, desc in sql_patterns:
            if re.search(pattern, code, re.IGNORECASE):
                findings.append(desc)
                confidence = max(confidence, conf)
        
        recommendations = [
            "Use parameterized queries with SQLAlchemy",
            "Avoid string concatenation in SQL queries",
            "Use ORM methods instead of raw SQL when possible",
            "Validate and sanitize all user inputs"
        ]
        
        return {
            "vulnerability": vuln,
            "specialized": "SQL Injection Analysis",
            "confidence": confidence,
            "findings": findings,
            "recommendations": recommendations[:2] if findings else []
        }

    async def _ssti_agent(self, code: str, vuln: str) -> Dict[str, Any]:
        """Specialized SSTI analysis."""
        findings = []
        confidence = 0.0
        
        # Look for SSTI patterns
        ssti_patterns = [
            (r'eval\s*\(', 0.95, "Direct eval() usage - critical SSTI risk"),
            (r'exec\s*\(', 0.95, "Direct exec() usage - critical SSTI risk"),
            (r'render_template_string\s*\([^)]*\+', 0.9, "Template string concatenation"),
            (r'Template\s*\([^)]*\{[^}]*\}', 0.8, "Direct variable injection in template"),
            (r'compile\s*\(', 0.7, "Dynamic code compilation"),
        ]
        
        for pattern, conf, desc in ssti_patterns:
            if re.search(pattern, code, re.IGNORECASE):
                findings.append(desc)
                confidence = max(confidence, conf)
        
        recommendations = [
            "Never use eval() or exec() with user input",
            "Use Jinja2 autoescaping for templates",
            "Validate and sanitize template inputs",
            "Use safe template rendering methods"
        ]
        
        return {
            "vulnerability": vuln,
            "specialized": "SSTI Analysis",
            "confidence": confidence,
            "findings": findings,
            "recommendations": recommendations[:2] if findings else []
        }

    async def _secret_agent(self, code: str, vuln: str) -> Dict[str, Any]:
        """Specialized secret detection."""
        findings = []
        confidence = 0.0
        
        # Look for hardcoded secrets
        secret_patterns = [
            (r'password\s*=\s*["\'][^"\'\n]{8,}["\']', 0.8, "Hardcoded password detected"),
            (r'api_key\s*=\s*["\'][^"\'\n]{16,}["\']', 0.9, "Hardcoded API key detected"),
            (r'secret\s*=\s*["\'][^"\'\n]{12,}["\']', 0.7, "Hardcoded secret detected"),
            (r'token\s*=\s*["\'][^"\'\n]{20,}["\']', 0.8, "Hardcoded token detected"),
            (r'["\'][A-Za-z0-9]{32,}["\']', 0.6, "Potential hardcoded credential"),
        ]
        
        for pattern, conf, desc in secret_patterns:
            matches = re.findall(pattern, code, re.IGNORECASE)
            if matches:
                findings.append(f"{desc} ({len(matches)} instances)")
                confidence = max(confidence, conf)
        
        recommendations = [
            "Move secrets to environment variables",
            "Use a secure secret management system",
            "Never commit secrets to version control",
            "Implement secret rotation policies"
        ]
        
        return {
            "vulnerability": vuln,
            "specialized": "Secret Detection Analysis",
            "confidence": confidence,
            "findings": findings,
            "recommendations": recommendations[:2] if findings else []
        }

    async def _auth_agent(self, code: str, vuln: str) -> Dict[str, Any]:
        """Specialized authentication analysis."""
        findings = []
        confidence = 0.0
        
        # Look for missing auth patterns
        auth_patterns = [
            (r'@app\.(get|post|put|delete)\s*\([^)]*\)\s*\ndef\s+\w+', 0.6, "Endpoint without visible authentication"),
            (r'def\s+(get_|post_|put_|delete_)\w+.*:', 0.5, "Function name suggests endpoint without auth decorator"),
            (r'return.*JSONResponse', 0.3, "Direct response without auth check"),
        ]
        
        # Check for auth decorators/middleware
        has_auth = bool(re.search(r'@.*auth|Depends\(.*auth|security=', code, re.IGNORECASE))
        
        if not has_auth:
            for pattern, conf, desc in auth_patterns:
                if re.search(pattern, code, re.IGNORECASE):
                    findings.append(desc)
                    confidence = max(confidence, conf)
        
        recommendations = [
            "Implement OAuth2 or JWT authentication",
            "Use FastAPI Depends() for auth injection",
            "Add authentication middleware",
            "Validate user permissions for each endpoint"
        ]
        
        return {
            "vulnerability": vuln,
            "specialized": "Authentication Analysis",
            "confidence": confidence,
            "findings": findings,
            "recommendations": recommendations[:2] if findings else []
        }

    async def _command_injection_agent(self, code: str, vuln: str) -> Dict[str, Any]:
        """Specialized command injection analysis."""
        findings = []
        confidence = 0.0
        
        # Look for command injection patterns
        cmd_patterns = [
            (r'subprocess\.(run|call|Popen)\s*\([^)]*shell\s*=\s*True', 0.9, "subprocess with shell=True"),
            (r'os\.system\s*\(', 0.9, "os.system() usage"),
            (r'os\.popen\s*\(', 0.8, "os.popen() usage"),
            (r'subprocess\.(run|call)\s*\([^)]*\+', 0.7, "String concatenation in subprocess"),
        ]
        
        for pattern, conf, desc in cmd_patterns:
            if re.search(pattern, code, re.IGNORECASE):
                findings.append(desc)
                confidence = max(confidence, conf)
        
        recommendations = [
            "Avoid shell=True in subprocess calls",
            "Use subprocess with argument lists instead of strings",
            "Validate and sanitize all command inputs",
            "Use safe alternatives to os.system()"
        ]
        
        return {
            "vulnerability": vuln,
            "specialized": "Command Injection Analysis",
            "confidence": confidence,
            "findings": findings,
            "recommendations": recommendations[:2] if findings else []
        }

    async def _deserialization_agent(self, code: str, vuln: str) -> Dict[str, Any]:
        """Specialized deserialization analysis."""
        findings = []
        confidence = 0.0
        
        # Look for insecure deserialization patterns
        deser_patterns = [
            (r'pickle\.loads?\s*\(', 0.9, "pickle.load() - unsafe deserialization"),
            (r'yaml\.load\s*\([^)]*(?!Loader=yaml\.SafeLoader)', 0.8, "yaml.load() without SafeLoader"),
            (r'marshal\.loads?\s*\(', 0.8, "marshal.load() usage"),
            (r'dill\.loads?\s*\(', 0.7, "dill.load() usage"),
        ]
        
        for pattern, conf, desc in deser_patterns:
            if re.search(pattern, code, re.IGNORECASE):
                findings.append(desc)
                confidence = max(confidence, conf)
        
        recommendations = [
            "Use json.loads() for safe deserialization",
            "Use yaml.safe_load() instead of yaml.load()",
            "Validate data before deserialization",
            "Avoid pickle with untrusted data"
        ]
        
        return {
            "vulnerability": vuln,
            "specialized": "Deserialization Analysis",
            "confidence": confidence,
            "findings": findings,
            "recommendations": recommendations[:2] if findings else []
        }

    async def _default_agent(self, code: str, vuln: str) -> Dict[str, Any]:
        """Default fallback agent."""
        return {
            "vulnerability": vuln,
            "specialized": "General Analysis",
            "confidence": 0.3,
            "findings": [f"Detected {vuln} - requires manual review"],
            "recommendations": ["Review code manually for security issues", "Follow security best practices"]
        }