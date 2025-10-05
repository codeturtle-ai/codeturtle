import ast
import logging
import re
from typing import List, Dict, Any

logger = logging.getLogger(__name__)

class ASTAnalyzer:
    """Production-grade static code analyzer using Python AST for vulnerability detection."""

    def __init__(self) -> None:
        self.findings: List[Dict[str, Any]] = []
        self.secret_patterns = [
            (r'(?i)(password|passwd|pwd)\s*=\s*["\'][^"\']{3,}["\']', 'hardcoded_password'),
            (r'(?i)(api[_-]?key|apikey)\s*=\s*["\'][^"\']{10,}["\']', 'hardcoded_api_key'),
            (r'(?i)(secret[_-]?key|secret)\s*=\s*["\'][^"\']{10,}["\']', 'hardcoded_secret'),
            (r'(?i)(token|auth[_-]?token)\s*=\s*["\'][^"\']{10,}["\']', 'hardcoded_token'),
            (r'(?i)(access[_-]?key|access_token)\s*=\s*["\'][^"\']{10,}["\']', 'hardcoded_access_key'),
        ]

    def analyze_code(self, code: str) -> List[Dict[str, Any]]:
        """Analyze code for security vulnerabilities using AST and regex patterns."""
        self.findings = []
        
        # Regex-based detection for secrets (works on raw code)
        self._check_secrets_regex(code)
        
        # AST-based detection
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
                "line": getattr(e, 'lineno', 0),
            })
        return self.findings

    def _check_secrets_regex(self, code: str) -> None:
        """Use regex to detect hardcoded secrets in raw code."""
        for pattern, vuln_type in self.secret_patterns:
            matches = re.finditer(pattern, code)
            for match in matches:
                line_num = code[:match.start()].count('\n') + 1
                self.findings.append({
                    "vulnerability": vuln_type,
                    "description": f"Hardcoded {vuln_type.replace('_', ' ')} detected",
                    "severity": "critical",
                    "confidence": 0.95,
                    "line": line_num,
                    "matched_text": match.group(0)[:50] + "..." if len(match.group(0)) > 50 else match.group(0),
                })

    def _walk_tree(self, node: ast.AST) -> None:
        """Walk AST tree and detect patterns."""
        if isinstance(node, (ast.Constant, ast.Str)):
            self._check_string_patterns(node)
        elif isinstance(node, ast.Call):
            self._check_dangerous_calls(node)
            self._check_sql_injection(node)
            self._check_command_injection(node)
            self._check_insecure_deserialization(node)
        elif isinstance(node, ast.FunctionDef):
            self._check_missing_auth(node)
            self._check_weak_crypto(node)
        elif isinstance(node, ast.Import) or isinstance(node, ast.ImportFrom):
            self._check_dangerous_imports(node)

        for child in ast.iter_child_nodes(node):
            self._walk_tree(child)

    def _check_string_patterns(self, node) -> None:
        """Check string constants for suspicious patterns."""
        try:
            if isinstance(node, ast.Constant) and isinstance(node.value, str):
                text = node.value
            elif isinstance(node, ast.Str):
                text = node.s
            else:
                return
                
            text_lower = text.lower()
            
            # Check for SQL keywords in strings (potential SQL injection)
            sql_keywords = ['select', 'insert', 'update', 'delete', 'drop', 'union']
            if any(keyword in text_lower for keyword in sql_keywords):
                if any(char in text for char in ['%s', '{', 'format']):
                    self.findings.append({
                        "vulnerability": "potential_sql_injection",
                        "description": "SQL query with string formatting detected",
                        "severity": "high",
                        "confidence": 0.7,
                        "line": node.lineno if hasattr(node, 'lineno') else 0,
                    })
        except Exception as e:
            logger.warning(f"Error checking string patterns: {e}")

    def _check_dangerous_calls(self, node: ast.Call) -> None:
        """Check for dangerous function calls (eval, exec, compile)."""
        dangerous_funcs = {
            'eval': ('code_execution', 'Use of eval() enables arbitrary code execution', 'critical', 0.95),
            'exec': ('code_execution', 'Use of exec() enables arbitrary code execution', 'critical', 0.95),
            'compile': ('code_execution', 'Use of compile() can lead to code execution', 'high', 0.85),
            '__import__': ('dangerous_import', 'Dynamic imports can be exploited', 'high', 0.8),
        }
        
        func_name = None
        if isinstance(node.func, ast.Name):
            func_name = node.func.id
        elif isinstance(node.func, ast.Attribute):
            func_name = node.func.attr
            
        if func_name in dangerous_funcs:
            vuln, desc, sev, conf = dangerous_funcs[func_name]
            self.findings.append({
                "vulnerability": vuln,
                "description": desc,
                "severity": sev,
                "confidence": conf,
                "line": node.lineno if hasattr(node, 'lineno') else 0,
                "function": func_name,
            })

    def _check_sql_injection(self, node: ast.Call) -> None:
        """Check for SQL injection patterns."""
        # Check for execute/executemany with string concatenation
        func_name = None
        if isinstance(node.func, ast.Attribute):
            func_name = node.func.attr
        elif isinstance(node.func, ast.Name):
            func_name = node.func.id
            
        if func_name in ['execute', 'executemany', 'raw']:
            for arg in node.args:
                # Check for string concatenation or f-strings
                if isinstance(arg, ast.BinOp) and isinstance(arg.op, ast.Add):
                    self.findings.append({
                        "vulnerability": "sql_injection",
                        "description": "SQL injection via string concatenation",
                        "severity": "critical",
                        "confidence": 0.9,
                        "line": node.lineno if hasattr(node, 'lineno') else 0,
                        "remediation": "Use parameterized queries instead",
                    })
                elif isinstance(arg, ast.JoinedStr):  # f-strings
                    self.findings.append({
                        "vulnerability": "sql_injection",
                        "description": "SQL injection via f-string formatting",
                        "severity": "critical",
                        "confidence": 0.85,
                        "line": node.lineno if hasattr(node, 'lineno') else 0,
                        "remediation": "Use parameterized queries instead of f-strings",
                    })

    def _check_command_injection(self, node: ast.Call) -> None:
        """Check for command injection vulnerabilities."""
        dangerous_os_funcs = ['system', 'popen', 'exec', 'spawn']
        
        if isinstance(node.func, ast.Attribute):
            if node.func.attr in dangerous_os_funcs:
                self.findings.append({
                    "vulnerability": "command_injection",
                    "description": f"Use of os.{node.func.attr}() can lead to command injection",
                    "severity": "critical",
                    "confidence": 0.85,
                    "line": node.lineno if hasattr(node, 'lineno') else 0,
                    "remediation": "Use subprocess with shell=False and list arguments",
                })
        elif isinstance(node.func, ast.Name):
            if node.func.id in ['system', 'popen']:
                self.findings.append({
                    "vulnerability": "command_injection",
                    "description": f"Use of {node.func.id}() can lead to command injection",
                    "severity": "critical",
                    "confidence": 0.85,
                    "line": node.lineno if hasattr(node, 'lineno') else 0,
                })

    def _check_insecure_deserialization(self, node: ast.Call) -> None:
        """Check for insecure deserialization."""
        dangerous_deserializers = {
            'pickle.load': ('Pickle deserialization', 'critical'),
            'pickle.loads': ('Pickle deserialization', 'critical'),
            'yaml.load': ('YAML deserialization without safe loader', 'high'),
            'marshal.load': ('Marshal deserialization', 'high'),
            'jsonpickle.decode': ('JSONPickle deserialization', 'high'),
        }
        
        func_str = ast.unparse(node.func) if hasattr(ast, 'unparse') else str(node.func)
        
        for dangerous_func, (desc, sev) in dangerous_deserializers.items():
            if dangerous_func in func_str:
                self.findings.append({
                    "vulnerability": "insecure_deserialization",
                    "description": f"{desc} can lead to remote code execution",
                    "severity": sev,
                    "confidence": 0.9,
                    "line": node.lineno if hasattr(node, 'lineno') else 0,
                    "remediation": "Use safe deserialization methods or validate input strictly",
                })

    def _check_missing_auth(self, node: ast.FunctionDef) -> None:
        """Check for missing authentication in API endpoints."""
        # Check for FastAPI/Flask route decorators without auth
        route_decorators = ['app.get', 'app.post', 'app.put', 'app.delete', 'app.patch', 'route']
        has_route = False
        has_auth = False
        
        for decorator in node.decorator_list:
            decorator_str = ast.unparse(decorator) if hasattr(ast, 'unparse') else ''
            if any(route in decorator_str.lower() for route in route_decorators):
                has_route = True
            if any(auth in decorator_str.lower() for auth in ['auth', 'require', 'login', 'permission']):
                has_auth = True
                
        if has_route and not has_auth:
            # Check function name for public endpoints
            public_patterns = ['health', 'ping', 'index', 'root', 'public', 'static']
            is_public = any(pattern in node.name.lower() for pattern in public_patterns)
            
            if not is_public:
                self.findings.append({
                    "vulnerability": "missing_authentication",
                    "description": f"API endpoint '{node.name}' may lack authentication",
                    "severity": "high",
                    "confidence": 0.6,
                    "line": node.lineno if hasattr(node, 'lineno') else 0,
                    "remediation": "Add authentication decorator or verify if endpoint should be public",
                })

    def _check_weak_crypto(self, node: ast.FunctionDef) -> None:
        """Check for weak cryptography usage."""
        weak_crypto_patterns = ['md5', 'sha1', 'des', 'rc4']
        func_body_str = ast.unparse(node) if hasattr(ast, 'unparse') else ''
        
        for weak_algo in weak_crypto_patterns:
            if weak_algo in func_body_str.lower():
                self.findings.append({
                    "vulnerability": "weak_cryptography",
                    "description": f"Use of weak cryptographic algorithm: {weak_algo.upper()}",
                    "severity": "medium",
                    "confidence": 0.7,
                    "line": node.lineno if hasattr(node, 'lineno') else 0,
                    "remediation": "Use SHA-256 or stronger algorithms",
                })

    def _check_dangerous_imports(self, node) -> None:
        """Check for imports of dangerous or deprecated modules."""
        dangerous_modules = {
            'pickle': ('Pickle module allows arbitrary code execution during deserialization', 'medium'),
            'shelve': ('Shelve uses pickle and is vulnerable to code execution', 'medium'),
            'marshal': ('Marshal module can execute arbitrary code', 'medium'),
            'tempfile': ('Tempfile usage can lead to race conditions', 'low'),
        }
        
        module_name = None
        if isinstance(node, ast.Import):
            module_name = node.names[0].name if node.names else None
        elif isinstance(node, ast.ImportFrom):
            module_name = node.module
            
        if module_name and module_name in dangerous_modules:
            desc, sev = dangerous_modules[module_name]
            self.findings.append({
                "vulnerability": "dangerous_import",
                "description": desc,
                "severity": sev,
                "confidence": 0.5,
                "line": node.lineno if hasattr(node, 'lineno') else 0,
                "module": module_name,
            })
