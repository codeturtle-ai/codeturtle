# Implementation Guide - FastAPI Security Agent

## 🚀 Quick Start Implementation

This guide provides step-by-step instructions for implementing the FastAPI Security Agent during the 6-hour hackathon sprint.

## 📋 Prerequisites Checklist

### Required Accounts & Access
- [ ] DigitalOcean account with Gradient AI Platform access
- [ ] GitHub account with API token
- [ ] Python 3.11+ development environment
- [ ] Git repository access
- [ ] Code editor (VS Code recommended)

### Development Tools
- [ ] Docker Desktop (for local development)
- [ ] Postman or similar API testing tool
- [ ] Redis (local or cloud instance)
- [ ] PostgreSQL (local or cloud instance)

## 🏗️ Hour-by-Hour Implementation

### Hour 1: Foundation Setup (0:00 - 1:00)

#### Step 1.1: Repository Setup (15 minutes)
```bash
# Create and initialize repository
mkdir fastapi-security-agent
cd fastapi-security-agent
git init
git remote add origin <your-repo-url>

# Create basic structure
mkdir -p {src,tests,docs,scripts,config}
mkdir -p src/{api,core,agents,analyzers,models}
```

#### Step 1.2: Basic Files Creation (15 minutes)
```bash
# Create essential files
touch {README.md,LICENSE,requirements.txt,.env,.gitignore}
touch {CONTRIBUTING.md,CODE_OF_CONDUCT.md}
```

**requirements.txt**:
```txt
fastapi==0.104.1
uvicorn[standard]==0.24.0
pydantic==2.5.0
httpx==0.25.2
redis==5.0.1
psycopg2-binary==2.9.9
sqlalchemy==2.0.23
alembic==1.13.0
celery==5.3.4
pytest==7.4.3
pytest-asyncio==0.21.1
python-multipart==0.0.6
python-jose[cryptography]==3.3.0
passlib[bcrypt]==1.7.4
```

#### Step 1.3: DigitalOcean Gradient AI Setup (20 minutes)
```python
# src/core/ai_client.py
import httpx
from typing import Dict, Any, List
import os

class GradientAIClient:
    def __init__(self):
        self.api_key = os.getenv("DIGITALOCEAN_AI_API_KEY")
        self.base_url = "https://api.digitalocean.com/v2/ai"
        self.client = httpx.AsyncClient()
    
    async def create_agent(self, agent_config: Dict[str, Any]) -> str:
        """Create a new AI agent for vulnerability detection"""
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        
        response = await self.client.post(
            f"{self.base_url}/agents",
            json=agent_config,
            headers=headers
        )
        return response.json()["agent_id"]
    
    async def query_agent(self, agent_id: str, query: str, context: str) -> Dict[str, Any]:
        """Query an AI agent with code context"""
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        
        payload = {
            "query": query,
            "context": context,
            "max_tokens": 1000
        }
        
        response = await self.client.post(
            f"{self.base_url}/agents/{agent_id}/query",
            json=payload,
            headers=headers
        )
        return response.json()
```

#### Step 1.4: Basic FastAPI App (10 minutes)
```python
# src/main.py
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import uvicorn

app = FastAPI(
    title="FastAPI Security Agent",
    description="AI-powered vulnerability detection for FastAPI applications",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class AnalysisRequest(BaseModel):
    pr_url: str
    options: dict = {}

@app.get("/health")
async def health_check():
    return {"status": "healthy", "service": "fastapi-security-agent"}

@app.post("/api/v1/analyze")
async def analyze_pr(request: AnalysisRequest):
    # Placeholder for Hour 2 implementation
    return {"status": "analysis_started", "pr_url": request.pr_url}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
```

---

### Hour 2: AI Agent Development (1:00 - 2:00)

#### Step 2.1: Agent Base Class (15 minutes)
```python
# src/agents/base_agent.py
from abc import ABC, abstractmethod
from typing import Dict, Any, List
from dataclasses import dataclass

@dataclass
class VulnerabilityFinding:
    type: str
    severity: str  # low, medium, high, critical
    confidence: float  # 0.0 to 1.0
    description: str
    line_number: int
    code_snippet: str
    remediation: str

class BaseAgent(ABC):
    def __init__(self, ai_client, agent_id: str):
        self.ai_client = ai_client
        self.agent_id = agent_id
        self.knowledge_base = self.load_knowledge_base()
    
    @abstractmethod
    def load_knowledge_base(self) -> Dict[str, Any]:
        """Load agent-specific knowledge base"""
        pass
    
    @abstractmethod
    async def analyze(self, code: str, context: Dict[str, Any]) -> List[VulnerabilityFinding]:
        """Analyze code for vulnerabilities"""
        pass
    
    async def query_ai(self, prompt: str, code_context: str) -> Dict[str, Any]:
        """Query the AI agent with specific prompt"""
        return await self.ai_client.query_agent(
            self.agent_id, 
            prompt, 
            code_context
        )
```

#### Step 2.2: SSTI Detection Agent (20 minutes)
```python
# src/agents/ssti_agent.py
from .base_agent import BaseAgent, VulnerabilityFinding
import re
import ast
from typing import Dict, Any, List

class SSTIAgent(BaseAgent):
    def load_knowledge_base(self) -> Dict[str, Any]:
        return {
            "dangerous_functions": [
                "render_template_string",
                "Template().render",
                "eval",
                "exec"
            ],
            "template_engines": ["jinja2", "django", "mako"],
            "patterns": [
                r"render_template_string\s*\([^)]*\+",  # String concatenation in templates
                r"Template\s*\([^)]*\{[^}]*\}",        # Direct variable injection
                r"\.render\s*\([^)]*request\.",        # Request data in render
            ]
        }
    
    async def analyze(self, code: str, context: Dict[str, Any]) -> List[VulnerabilityFinding]:
        findings = []
        
        # Static pattern matching
        for pattern in self.knowledge_base["patterns"]:
            matches = re.finditer(pattern, code, re.MULTILINE)
            for match in matches:
                line_num = code[:match.start()].count('\n') + 1
                
                # Query AI for detailed analysis
                ai_prompt = f"""
                Analyze this code snippet for Server-Side Template Injection vulnerabilities:
                
                Code: {match.group()}
                Context: FastAPI application
                
                Provide:
                1. Vulnerability assessment (0-10 severity)
                2. Confidence level (0-1)
                3. Detailed explanation
                4. Remediation steps
                """
                
                ai_response = await self.query_ai(ai_prompt, code)
                
                if ai_response.get("vulnerability_detected", False):
                    findings.append(VulnerabilityFinding(
                        type="SSTI",
                        severity=ai_response.get("severity", "medium"),
                        confidence=ai_response.get("confidence", 0.7),
                        description=ai_response.get("description", "Potential SSTI vulnerability"),
                        line_number=line_num,
                        code_snippet=match.group(),
                        remediation=ai_response.get("remediation", "Use safe template rendering")
                    ))
        
        return findings
```

#### Step 2.3: Agent Factory and Router (15 minutes)
```python
# src/agents/agent_factory.py
from .ssti_agent import SSTIAgent
from .sql_injection_agent import SQLInjectionAgent
from .secret_detection_agent import SecretDetectionAgent
from .error_handling_agent import ErrorHandlingAgent
from typing import List, Dict, Any

class AgentFactory:
    def __init__(self, ai_client):
        self.ai_client = ai_client
        self.agents = {}
    
    async def initialize_agents(self):
        """Initialize all specialized agents"""
        agent_configs = {
            "ssti": {
                "name": "SSTI Detection Agent",
                "description": "Detects Server-Side Template Injection vulnerabilities",
                "knowledge_base": "fastapi_ssti_patterns"
            },
            "sql_injection": {
                "name": "SQL Injection Agent", 
                "description": "Detects SQL injection vulnerabilities",
                "knowledge_base": "sql_injection_patterns"
            },
            "secret_detection": {
                "name": "Secret Detection Agent",
                "description": "Detects hardcoded secrets and credentials",
                "knowledge_base": "secret_patterns"
            },
            "error_handling": {
                "name": "Error Handling Agent",
                "description": "Detects missing or improper error handling",
                "knowledge_base": "error_handling_patterns"
            }
        }
        
        for agent_type, config in agent_configs.items():
            agent_id = await self.ai_client.create_agent(config)
            
            if agent_type == "ssti":
                self.agents[agent_type] = SSTIAgent(self.ai_client, agent_id)
            elif agent_type == "sql_injection":
                self.agents[agent_type] = SQLInjectionAgent(self.ai_client, agent_id)
            # ... initialize other agents
    
    def get_relevant_agents(self, code: str) -> List[str]:
        """Determine which agents should analyze the code"""
        relevant_agents = []
        
        # Simple heuristics for agent selection
        if any(keyword in code.lower() for keyword in ["template", "render", "jinja"]):
            relevant_agents.append("ssti")
        
        if any(keyword in code.lower() for keyword in ["query", "execute", "sql"]):
            relevant_agents.append("sql_injection")
        
        if any(keyword in code.lower() for keyword in ["api_key", "password", "secret"]):
            relevant_agents.append("secret_detection")
        
        # Always check error handling
        relevant_agents.append("error_handling")
        
        return relevant_agents
```

#### Step 2.4: Knowledge Base Setup (10 minutes)
```python
# src/core/knowledge_base.py
from typing import Dict, Any, List
import json

class KnowledgeBase:
    def __init__(self):
        self.vulnerability_patterns = self.load_patterns()
        self.remediation_guides = self.load_remediation_guides()
    
    def load_patterns(self) -> Dict[str, List[str]]:
        """Load vulnerability detection patterns"""
        return {
            "ssti": [
                "render_template_string with user input",
                "Template() with unescaped variables",
                "Direct string formatting in templates"
            ],
            "sql_injection": [
                "String concatenation in SQL queries",
                "f-strings with user input in SQL",
                "Raw SQL execution without parameters"
            ],
            "secrets": [
                "Hardcoded API keys",
                "Database URLs with credentials",
                "JWT secrets in code"
            ],
            "error_handling": [
                "Unhandled exceptions in routes",
                "Detailed error messages to users",
                "Missing input validation"
            ]
        }
    
    def load_remediation_guides(self) -> Dict[str, str]:
        """Load remediation guidance for each vulnerability type"""
        return {
            "ssti": "Use Jinja2 autoescaping, validate template inputs, avoid render_template_string",
            "sql_injection": "Use parameterized queries, ORM methods, input validation",
            "secrets": "Use environment variables, secret management systems, rotate keys",
            "error_handling": "Implement proper exception handling, log errors securely, validate inputs"
        }
    
    def get_pattern_examples(self, vulnerability_type: str) -> List[str]:
        """Get example patterns for a vulnerability type"""
        return self.vulnerability_patterns.get(vulnerability_type, [])
    
    def get_remediation(self, vulnerability_type: str) -> str:
        """Get remediation guidance for a vulnerability type"""
        return self.remediation_guides.get(vulnerability_type, "Follow security best practices")
```

---

### Hour 3: Enhanced Detection Engine (2:00 - 3:00)

#### Step 3.1: Static Analysis Engine (20 minutes)
```python
# src/analyzers/static_analyzer.py
import ast
import re
from typing import List, Dict, Any
from dataclasses import dataclass

@dataclass
class StaticFinding:
    type: str
    severity: str
    line_number: int
    description: str
    code_snippet: str

class StaticAnalyzer:
    def __init__(self):
        self.rules = self.load_rules()
    
    def load_rules(self) -> Dict[str, Any]:
        """Load static analysis rules"""
        return {
            "dangerous_functions": [
                "eval", "exec", "compile", "__import__"
            ],
            "sql_patterns": [
                r"\.execute\s*\([^)]*\+",  # String concatenation in execute
                r"f[\"'].*SELECT.*{.*}",   # f-string in SQL
                r"\".*SELECT.*\".*%",     # String formatting in SQL
            ],
            "secret_patterns": [
                r"api_key\s*=\s*[\"'][^\"']+[\"']",
                r"password\s*=\s*[\"'][^\"']+[\"']",
                r"secret\s*=\s*[\"'][^\"']+[\"']",
                r"token\s*=\s*[\"'][^\"']+[\"']",
            ]
        }
    
    def analyze_ast(self, code: str) -> List[StaticFinding]:
        """Analyze code using AST parsing"""
        findings = []
        
        try:
            tree = ast.parse(code)
            
            for node in ast.walk(tree):
                # Check for dangerous function calls
                if isinstance(node, ast.Call):
                    if isinstance(node.func, ast.Name):
                        if node.func.id in self.rules["dangerous_functions"]:
                            findings.append(StaticFinding(
                                type="dangerous_function",
                                severity="high",
                                line_number=node.lineno,
                                description=f"Use of dangerous function: {node.func.id}",
                                code_snippet=ast.unparse(node)
                            ))
                
                # Check for hardcoded strings that might be secrets
                if isinstance(node, ast.Assign):
                    for target in node.targets:
                        if isinstance(target, ast.Name):
                            if any(secret_word in target.id.lower() 
                                  for secret_word in ["key", "password", "secret", "token"]):
                                if isinstance(node.value, ast.Constant):
                                    findings.append(StaticFinding(
                                        type="hardcoded_secret",
                                        severity="medium",
                                        line_number=node.lineno,
                                        description=f"Potential hardcoded secret: {target.id}",
                                        code_snippet=ast.unparse(node)
                                    ))
        
        except SyntaxError:
            # Handle syntax errors gracefully
            pass
        
        return findings
    
    def analyze_patterns(self, code: str) -> List[StaticFinding]:
        """Analyze code using regex patterns"""
        findings = []
        
        # Check SQL injection patterns
        for pattern in self.rules["sql_patterns"]:
            matches = re.finditer(pattern, code, re.MULTILINE | re.IGNORECASE)
            for match in matches:
                line_num = code[:match.start()].count('\n') + 1
                findings.append(StaticFinding(
                    type="sql_injection",
                    severity="high",
                    line_number=line_num,
                    description="Potential SQL injection vulnerability",
                    code_snippet=match.group()
                ))
        
        # Check secret patterns
        for pattern in self.rules["secret_patterns"]:
            matches = re.finditer(pattern, code, re.MULTILINE | re.IGNORECASE)
            for match in matches:
                line_num = code[:match.start()].count('\n') + 1
                findings.append(StaticFinding(
                    type="hardcoded_secret",
                    severity="medium",
                    line_number=line_num,
                    description="Potential hardcoded secret",
                    code_snippet=match.group()
                ))
        
        return findings
    
    def analyze(self, code: str) -> List[StaticFinding]:
        """Run complete static analysis"""
        ast_findings = self.analyze_ast(code)
        pattern_findings = self.analyze_patterns(code)
        return ast_findings + pattern_findings
```

#### Step 3.2: Combined Analysis Engine (25 minutes)
```python
# src/core/analysis_engine.py
from typing import List, Dict, Any
from ..analyzers.static_analyzer import StaticAnalyzer, StaticFinding
from ..agents.agent_factory import AgentFactory
from ..agents.base_agent import VulnerabilityFinding
from dataclasses import dataclass
import asyncio

@dataclass
class CombinedFinding:
    id: str
    type: str
    severity: str
    confidence: float
    description: str
    line_number: int
    code_snippet: str
    remediation: str
    sources: List[str]  # ["static", "ai_agent_name"]
    ai_confidence: float = 0.0
    static_confidence: float = 0.0

class AnalysisEngine:
    def __init__(self, ai_client):
        self.static_analyzer = StaticAnalyzer()
        self.agent_factory = AgentFactory(ai_client)
        self.scoring_weights = {
            "static": 0.3,
            "ai": 0.7,
            "combined_bonus": 0.2  # Bonus when both detect same issue
        }
    
    async def initialize(self):
        """Initialize the analysis engine"""
        await self.agent_factory.initialize_agents()
    
    async def analyze_code(self, code: str, context: Dict[str, Any] = None) -> List[CombinedFinding]:
        """Run combined static and AI analysis"""
        if context is None:
            context = {}
        
        # Run static analysis
        static_findings = self.static_analyzer.analyze(code)
        
        # Determine relevant AI agents
        relevant_agents = self.agent_factory.get_relevant_agents(code)
        
        # Run AI analysis with relevant agents
        ai_findings = []
        for agent_name in relevant_agents:
            if agent_name in self.agent_factory.agents:
                agent = self.agent_factory.agents[agent_name]
                agent_findings = await agent.analyze(code, context)
                ai_findings.extend(agent_findings)
        
        # Combine and score findings
        combined_findings = self.combine_findings(static_findings, ai_findings)
        
        return combined_findings
    
    def combine_findings(self, static_findings: List[StaticFinding], 
                        ai_findings: List[VulnerabilityFinding]) -> List[CombinedFinding]:
        """Combine static and AI findings with intelligent scoring"""
        combined = []
        finding_id = 0
        
        # Process static findings
        for static_finding in static_findings:
            finding_id += 1
            combined.append(CombinedFinding(
                id=f"finding_{finding_id}",
                type=static_finding.type,
                severity=static_finding.severity,
                confidence=0.6,  # Base confidence for static analysis
                description=static_finding.description,
                line_number=static_finding.line_number,
                code_snippet=static_finding.code_snippet,
                remediation="Follow security best practices",
                sources=["static"],
                static_confidence=0.6
            ))
        
        # Process AI findings
        for ai_finding in ai_findings:
            finding_id += 1
            
            # Check if this finding correlates with a static finding
            correlated_static = self.find_correlated_static_finding(
                ai_finding, static_findings
            )
            
            if correlated_static:
                # Enhance existing finding with AI insights
                existing_finding = next(
                    (f for f in combined if f.line_number == correlated_static.line_number 
                     and f.type == correlated_static.type), None
                )
                
                if existing_finding:
                    # Boost confidence when both static and AI detect same issue
                    existing_finding.confidence = min(1.0, 
                        existing_finding.confidence + ai_finding.confidence * 0.3
                    )
                    existing_finding.sources.append("ai")
                    existing_finding.ai_confidence = ai_finding.confidence
                    existing_finding.description = ai_finding.description
                    existing_finding.remediation = ai_finding.remediation
                    continue
            
            # Add as new AI-only finding
            combined.append(CombinedFinding(
                id=f"finding_{finding_id}",
                type=ai_finding.type,
                severity=ai_finding.severity,
                confidence=ai_finding.confidence,
                description=ai_finding.description,
                line_number=ai_finding.line_number,
                code_snippet=ai_finding.code_snippet,
                remediation=ai_finding.remediation,
                sources=["ai"],
                ai_confidence=ai_finding.confidence
            ))
        
        # Sort by confidence and severity
        combined.sort(key=lambda x: (
            self.severity_to_score(x.severity), 
            x.confidence
        ), reverse=True)
        
        return combined
    
    def find_correlated_static_finding(self, ai_finding: VulnerabilityFinding, 
                                     static_findings: List[StaticFinding]) -> StaticFinding:
        """Find static finding that correlates with AI finding"""
        for static_finding in static_findings:
            # Check if they're on the same line or nearby lines
            if abs(static_finding.line_number - ai_finding.line_number) <= 2:
                # Check if they're the same type of vulnerability
                if self.vulnerability_types_match(static_finding.type, ai_finding.type):
                    return static_finding
        return None
    
    def vulnerability_types_match(self, static_type: str, ai_type: str) -> bool:
        """Check if vulnerability types from different analyzers match"""
        type_mappings = {
            "sql_injection": ["sql_injection", "sqli"],
            "hardcoded_secret": ["secret_detection", "secrets"],
            "dangerous_function": ["code_injection", "dangerous_calls"],
            "ssti": ["ssti", "template_injection"]
        }
        
        for canonical_type, variants in type_mappings.items():
            if static_type in variants and ai_type in variants:
                return True
        
        return static_type.lower() == ai_type.lower()
    
    def severity_to_score(self, severity: str) -> int:
        """Convert severity to numeric score for sorting"""
        severity_scores = {
            "critical": 4,
            "high": 3,
            "medium": 2,
            "low": 1
        }
        return severity_scores.get(severity.lower(), 0)
```

#### Step 3.3: Scoring Algorithm (15 minutes)
```python
# src/core/scoring.py
from typing import List, Dict, Any
from .analysis_engine import CombinedFinding
import math

class VulnerabilityScorer:
    def __init__(self):
        self.severity_weights = {
            "critical": 10.0,
            "high": 7.5,
            "medium": 5.0,
            "low": 2.5
        }
        
        self.confidence_threshold = 0.6
        self.max_score = 100.0
    
    def calculate_risk_score(self, findings: List[CombinedFinding]) -> Dict[str, Any]:
        """Calculate overall risk score for the analyzed code"""
        if not findings:
            return {
                "overall_score": 0.0,
                "risk_level": "low",
                "total_findings": 0,
                "high_confidence_findings": 0,
                "breakdown": {}
            }
        
        # Filter high-confidence findings
        high_confidence_findings = [
            f for f in findings if f.confidence >= self.confidence_threshold
        ]
        
        # Calculate weighted score
        total_weighted_score = 0.0
        severity_breakdown = {"critical": 0, "high": 0, "medium": 0, "low": 0}
        
        for finding in high_confidence_findings:
            severity_weight = self.severity_weights.get(finding.severity.lower(), 1.0)
            confidence_multiplier = finding.confidence
            
            # Bonus for findings detected by multiple sources
            source_bonus = 1.2 if len(finding.sources) > 1 else 1.0
            
            finding_score = severity_weight * confidence_multiplier * source_bonus
            total_weighted_score += finding_score
            
            severity_breakdown[finding.severity.lower()] += 1
        
        # Normalize score to 0-100 scale
        normalized_score = min(self.max_score, 
                             (total_weighted_score / len(findings)) * 10)
        
        # Determine risk level
        risk_level = self.determine_risk_level(normalized_score, severity_breakdown)
        
        return {
            "overall_score": round(normalized_score, 2),
            "risk_level": risk_level,
            "total_findings": len(findings),
            "high_confidence_findings": len(high_confidence_findings),
            "breakdown": severity_breakdown,
            "recommendations": self.generate_recommendations(findings)
        }
    
    def determine_risk_level(self, score: float, breakdown: Dict[str, int]) -> str:
        """Determine risk level based on score and finding breakdown"""
        if breakdown["critical"] > 0 or score >= 80:
            return "critical"
        elif breakdown["high"] > 2 or score >= 60:
            return "high"
        elif breakdown["medium"] > 3 or score >= 30:
            return "medium"
        else:
            return "low"
    
    def generate_recommendations(self, findings: List[CombinedFinding]) -> List[str]:
        """Generate prioritized recommendations based on findings"""
        recommendations = []
        
        # Group findings by type
        finding_types = {}
        for finding in findings:
            if finding.type not in finding_types:
                finding_types[finding.type] = []
            finding_types[finding.type].append(finding)
        
        # Generate type-specific recommendations
        for vuln_type, type_findings in finding_types.items():
            if len(type_findings) > 1:
                recommendations.append(
                    f"Address {len(type_findings)} {vuln_type} vulnerabilities - "
                    f"this appears to be a systemic issue"
                )
            else:
                recommendations.append(
                    f"Fix {vuln_type} vulnerability on line {type_findings[0].line_number}"
                )
        
        # Add general recommendations
        if len(findings) > 5:
            recommendations.append(
                "Consider implementing automated security testing in your CI/CD pipeline"
            )
        
        return recommendations[:5]  # Limit to top 5 recommendations
```

---

### Hour 4: Web Interface & Demo (3:00 - 4:00)

#### Step 4.1: Enhanced API Endpoints (20 minutes)
```python
# src/api/routes.py
from fastapi import APIRouter, HTTPException, BackgroundTasks
from pydantic import BaseModel, HttpUrl
from typing import Optional, Dict, Any
import uuid
from ..core.analysis_engine import AnalysisEngine
from ..core.scoring import VulnerabilityScorer
from ..core.github_client import GitHubClient

router = APIRouter(prefix="/api/v1")

class AnalysisRequest(BaseModel):
    pr_url: HttpUrl
    options: Dict[str, Any] = {}

class BatchAnalysisRequest(BaseModel):
    repository: str
    branch: str = "main"
    max_prs: int = 10

class AnalysisResponse(BaseModel):
    analysis_id: str
    status: str
    pr_url: str
    findings_count: int
    risk_score: float
    risk_level: str

# In-memory storage for demo (use Redis/DB in production)
analysis_results = {}

@router.post("/analyze", response_model=AnalysisResponse)
async def analyze_pr(request: AnalysisRequest, background_tasks: BackgroundTasks):
    """Analyze a single GitHub PR for vulnerabilities"""
    analysis_id = str(uuid.uuid4())
    
    # Start background analysis
    background_tasks.add_task(
        run_pr_analysis, 
        analysis_id, 
        str(request.pr_url), 
        request.options
    )
    
    # Return immediate response
    analysis_results[analysis_id] = {
        "status": "running",
        "pr_url": str(request.pr_url),
        "findings": [],
        "risk_score": 0.0
    }
    
    return AnalysisResponse(
        analysis_id=analysis_id,
        status="running",
        pr_url=str(request.pr_url),
        findings_count=0,
        risk_score=0.0,
        risk_level="unknown"
    )

@router.get("/analysis/{analysis_id}")
async def get_analysis_result(analysis_id: str):
    """Get analysis results by ID"""
    if analysis_id not in analysis_results:
        raise HTTPException(status_code=404, detail="Analysis not found")
    
    return analysis_results[analysis_id]

@router.post("/batch-analyze")
async def batch_analyze(request: BatchAnalysisRequest, background_tasks: BackgroundTasks):
    """Analyze multiple PRs from a repository"""
    batch_id = str(uuid.uuid4())
    
    background_tasks.add_task(
        run_batch_analysis,
        batch_id,
        request.repository,
        request.branch,
        request.max_prs
    )
    
    return {"batch_id": batch_id, "status": "started"}

async def run_pr_analysis(analysis_id: str, pr_url: str, options: Dict[str, Any]):
    """Background task to run PR analysis"""
    try:
        # Initialize components
        github_client = GitHubClient()
        analysis_engine = AnalysisEngine(ai_client=None)  # Initialize with actual AI client
        scorer = VulnerabilityScorer()
        
        await analysis_engine.initialize()
        
        # Fetch PR data
        pr_data = await github_client.get_pr_data(pr_url)
        
        # Analyze each changed file
        all_findings = []
        for file_change in pr_data["files"]:
            if file_change["filename"].endswith(".py"):
                findings = await analysis_engine.analyze_code(
                    file_change["patch"], 
                    {"filename": file_change["filename"]}
                )
                all_findings.extend(findings)
        
        # Calculate risk score
        risk_assessment = scorer.calculate_risk_score(all_findings)
        
        # Update results
        analysis_results[analysis_id] = {
            "status": "completed",
            "pr_url": pr_url,
            "findings": [finding.__dict__ for finding in all_findings],
            "risk_score": risk_assessment["overall_score"],
            "risk_level": risk_assessment["risk_level"],
            "recommendations": risk_assessment["recommendations"],
            "summary": {
                "total_findings": len(all_findings),
                "high_confidence_findings": risk_assessment["high_confidence_findings"],
                "breakdown": risk_assessment["breakdown"]
            }
        }
        
    except Exception as e:
        analysis_results[analysis_id] = {
            "status": "failed",
            "error": str(e),
            "pr_url": pr_url
        }

async def run_batch_analysis(batch_id: str, repository: str, branch: str, max_prs: int):
    """Background task to run batch analysis"""
    # Implementation for batch analysis
    pass
```

#### Step 4.2: GitHub Client (15 minutes)
```python
# src/core/github_client.py
import httpx
import re
from typing import Dict, Any, List
import os

class GitHubClient:
    def __init__(self):
        self.token = os.getenv("GITHUB_TOKEN")
        self.base_url = "https://api.github.com"
        self.client = httpx.AsyncClient(
            headers={"Authorization": f"token {self.token}"}
        )
    
    async def get_pr_data(self, pr_url: str) -> Dict[str, Any]:
        """Extract PR data from GitHub API"""
        # Parse PR URL to get owner, repo, and PR number
        match = re.match(
            r"https://github\.com/([^/]+)/([^/]+)/pull/(\d+)", 
            pr_url
        )
        
        if not match:
            raise ValueError("Invalid GitHub PR URL")
        
        owner, repo, pr_number = match.groups()
        
        # Fetch PR details
        pr_response = await self.client.get(
            f"{self.base_url}/repos/{owner}/{repo}/pulls/{pr_number}"
        )
        pr_data = pr_response.json()
        
        # Fetch PR files
        files_response = await self.client.get(
            f"{self.base_url}/repos/{owner}/{repo}/pulls/{pr_number}/files"
        )
        files_data = files_response.json()
        
        return {
            "pr": pr_data,
            "files": files_data,
            "owner": owner,
            "repo": repo,
            "number": pr_number
        }
    
    async def get_repository_prs(self, repository: str, state: str = "open", 
                                max_count: int = 10) -> List[Dict[str, Any]]:
        """Get recent PRs from a repository"""
        owner, repo = repository.split("/")
        
        response = await self.client.get(
            f"{self.base_url}/repos/{owner}/{repo}/pulls",
            params={"state": state, "per_page": max_count}
        )
        
        return response.json()
```

#### Step 4.3: Simple Web UI (25 minutes)
```python
# src/api/web_routes.py
from fastapi import APIRouter, Request, Form
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
import httpx

web_router = APIRouter()
templates = Jinja2Templates(directory="templates")

@web_router.get("/", response_class=HTMLResponse)
async def home(request: Request):
    """Home page with analysis form"""
    return templates.TemplateResponse("index.html", {"request": request})

@web_router.post("/analyze-web", response_class=HTMLResponse)
async def analyze_web(request: Request, pr_url: str = Form(...)):
    """Web form submission for PR analysis"""
    # Call the API endpoint
    async with httpx.AsyncClient() as client:
        response = await client.post(
            "http://localhost:8000/api/v1/analyze",
            json={"pr_url": pr_url}
        )
        analysis_data = response.json()
    
    return templates.TemplateResponse(
        "analysis_result.html", 
        {"request": request, "analysis": analysis_data}
    )

@web_router.get("/dashboard", response_class=HTMLResponse)
async def dashboard(request: Request):
    """Dashboard showing recent analyses"""
    return templates.TemplateResponse("dashboard.html", {"request": request})
```

Create templates directory and basic HTML templates:

```html
<!-- templates/index.html -->
<!DOCTYPE html>
<html>
<head>
    <title>FastAPI Security Agent</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/css/bootstrap.min.css" rel="stylesheet">
</head>
<body>
    <div class="container mt-5">
        <h1>FastAPI Security Agent</h1>
        <p class="lead">AI-powered vulnerability detection for FastAPI applications</p>
        
        <form method="post" action="/analyze-web" class="mt-4">
            <div class="mb-3">
                <label for="pr_url" class="form-label">GitHub PR URL</label>
                <input type="url" class="form-control" id="pr_url" name="pr_url" 
                       placeholder="https://github.com/owner/repo/pull/123" required>
            </div>
            <button type="submit" class="btn btn-primary">Analyze PR</button>
        </form>
        
        <div class="mt-5">
            <h3>Features</h3>
            <ul>
                <li>AI-powered vulnerability detection</li>
                <li>FastAPI-specific security rules</li>
                <li>Real-time analysis</li>
                <li>Detailed remediation guidance</li>
            </ul>
        </div>
    </div>
</body>
</html>
```

---

This implementation guide provides a solid foundation for the 6-hour hackathon sprint. Each hour builds upon the previous work, creating a comprehensive AI-powered security analysis tool that leverages DigitalOcean's Gradient AI Platform.

The remaining hours (5 and 6) would focus on:
- **Hour 5**: Running large-scale analysis, generating evidence, and creating visualizations
- **Hour 6**: Creating demo materials, documentation, and final presentation

This implementation demonstrates deep AI integration, practical utility, and professional execution - key criteria for winning the hackathon.