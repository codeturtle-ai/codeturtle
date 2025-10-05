import ast
import logging
from typing import List, Dict, Any

logger = logging.getLogger(__name__)

class ASTAnalyzer:
    """Static code analyzer using Python AST for vulnerability detection."""

    def __init__(self) -> None:
        self.findings: List[Dict[str, Any]] = []

    def analyze_code(self, code: str) -> List[Dict[str, Any]]:
        """Analyze code for security vulnerabilities using AST."""
        self.findings = []
        try:
            tree = ast.parse(code, mode='exec')
            self._walk_tree(tree)
        except SyntaxError as e:
            logger.warning(f"Syntax error in code: {e}")
            self.findings.append({
                "vulnerability": "syntax_error",
                "description": "Code contains syntax errors",
                "severity": "low",
                "confidence": 1.0,
            })
        return self.findings

    def _walk_tree(self, node: ast.AST) -> None:
        """Walk AST tree and detect patterns."""
        if isinstance(node, ast.Str):
            self._check_hardcoded_secret(node)
        elif isinstance(node, ast.Call):
            self._check_sql_injection(node)
            self._check_ssti(node)
            self._check_insecure_deserialization(node)
        elif isinstance(node, ast.FunctionDef):
            self._check_missing_auth(node)

        for child in ast.iter_child_nodes(node):
            self._walk_tree(child)

    def _check_hardcoded_secret(self, node: ast.Str) -> None:
        """Check for hardcoded secrets in string literals."""
        text = node.s.lower()
        if any(keyword in text for keyword in ['password=', 'secret=', 'key=', 'token=']):
            self.findings.append({
                "vulnerability": "hardcoded_secret",
                "description": "Potential hardcoded secret found",
                "severity": "high",
                "confidence": 0.7,
            })

    def _check_sql_injection(self, node: ast.Call) -> None:
        """Check for SQL injection patterns."""
        if isinstance(node.func, ast.Name) and node.func.id in ['execute', 'executemany']:
            # Check if query is concatenated with variables
            for arg in node.args:
                if isinstance(arg, ast.BinOp) and isinstance(arg.op, ast.Add):
                    self.findings.append({
                        "vulnerability": "sql_injection",
                        "description": "Potential SQL injection via string concatenation",
                        "severity": "high",
                        "confidence": 0.8,
                    })
                    break

    def _check_ssti(self, node: ast.Call) -> None:
        """Check for Server-Side Template Injection."""
        if isinstance(node.func, ast.Name) and node.func.id in ['eval', 'exec']:
            self.findings.append({
                "vulnerability": "ssti",
                "description": "Use of eval/exec can lead to code execution",
                "severity": "critical",
                "confidence": 0.9,
            })

    def _check_insecure_deserialization(self, node: ast.Call) -> None:
        """Check for insecure deserialization."""
        if isinstance(node.func, ast.Name) and node.func.id in ['pickle.load', 'pickle.loads', 'yaml.load']:
            self.findings.append({
                "vulnerability": "insecure_deserialization",
                "description": "Insecure deserialization can lead to remote code execution",
                "severity": "high",
                "confidence": 0.8,
            })

    def _check_missing_auth(self, node: ast.FunctionDef) -> None:
        """Check for missing authentication in endpoints."""
        # Simple heuristic: check if function name suggests endpoint and lacks auth decorator
        if node.name.startswith(('get_', 'post_', 'put_', 'delete_')):
            has_auth = any(
                isinstance(decorator, ast.Name) and 'auth' in decorator.id.lower()
                for decorator in node.decorator_list
            )
            if not has_auth:
                self.findings.append({
                    "vulnerability": "missing_auth",
                    "description": "Endpoint may lack proper authentication",
                    "severity": "medium",
                    "confidence": 0.6,
                })
