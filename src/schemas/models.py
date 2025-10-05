import re
from typing import List

from pydantic import BaseModel, Field, field_validator

class PRAnalysisRequest(BaseModel):
    url: str = Field(..., description="GitHub PR URL")
    max_prs: int = Field(30, ge=1, le=50, description="Limit number of PRs to analyze")

    @field_validator('url')
    @classmethod
    def validate_github_pr_url(cls, v: str) -> str:
        """Validate GitHub PR URL format."""
        github_pr_pattern = r'^https://github\.com/[^/]+/[^/]+/pull/\d+$'
        if not re.match(github_pr_pattern, v):
            raise ValueError('Invalid GitHub PR URL format. Expected: https://github.com/owner/repo/pull/number')
        return v

class VulnerabilityReport(BaseModel):
    pr_url: str
    vulnerabilities: List[str]
    risk_score: float
    recommendations: List[str]
    summary: str = "Analysis completed"
