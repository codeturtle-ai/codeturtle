from pydantic import BaseModel, Field
from typing import List

class PRAnalysisRequest(BaseModel):
    url: str = Field(..., description="GitHub PR URL")
    max_prs: int = Field(30, ge=1, le=50, description="Limit number of PRs to analyze")

class VulnerabilityReport(BaseModel):
    pr_url: str
    vulnerabilities: List[str]
    risk_score: float
    recommendations: List[str]
