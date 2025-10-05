from typing import Dict, List, Any

class FastAPISecurityKB:
    """Knowledge base for FastAPI security vulnerabilities with retrieval."""
    
    def __init__(self) -> None:
        self.knowledge: Dict[str, Dict[str, Any]] = {
            "sql_injection": {
                "patterns": ["SELECT", "INSERT", "UPDATE", "DELETE", "WHERE", "f-string in query"],
                "description": "SQL injection occurs when untrusted input is concatenated into SQL queries.",
                "remediation": "Use parameterized queries or ORM features like SQLAlchemy.",
                "severity": "high",
            },
            "ssti": {
                "patterns": ["eval(", "exec(", "Template.render(", "jinja2"],
                "description": "Server-Side Template Injection allows code execution via template inputs.",
                "remediation": "Sanitize inputs and avoid dynamic template execution.",
                "severity": "critical",
            },
            "hardcoded_secret": {
                "patterns": ["password=", "secret=", "key=", "token="],
                "description": "Secrets embedded in code can be exposed in repositories or logs.",
                "remediation": "Store secrets in environment variables or secure vaults.",
                "severity": "high",
            },
            "missing_auth": {
                "patterns": ["@app.get(", "@app.post(", "no auth"],
                "description": "Endpoints without authentication allow unauthorized access.",
                "remediation": "Implement OAuth2, JWT, or API keys.",
                "severity": "medium",
            },
            "insecure_deserialization": {
                "patterns": ["pickle.load", "json.loads", "yaml.load"],
                "description": "Deserializing untrusted data can lead to remote code execution.",
                "remediation": "Use safe deserialization methods or validate inputs.",
                "severity": "high",
            },
        }

    def retrieve(self, query: str) -> List[Dict[str, Any]]:
        """Retrieve relevant knowledge based on query keywords."""
        query_lower = query.lower()
        matches = []
        for key, data in self.knowledge.items():
            if any(pattern.lower() in query_lower for pattern in data["patterns"]):
                matches.append({"vulnerability": key, **data})
        return matches[:3]  # Limit to top 3 matches
