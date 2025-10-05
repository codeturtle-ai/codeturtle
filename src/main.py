"""
FastAPI Security Agent - Main application entry point.

This module adapts the existing Magnet POC for smaller-scale analysis
(20-30 PRs) with enhanced error handling and AI integration.
"""

import asyncio
import logging
from typing import List, Optional

import uvicorn
from fastapi import FastAPI, HTTPException, Request, Form
from fastapi.templating import Jinja2Templates
from fastapi.responses import JSONResponse
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from pydantic import BaseModel

# Local modules
from schemas.models import PRAnalysisRequest, VulnerabilityReport
from schemas.config import config
from clients.gradient_ai import GradientAIClient
from ai.agent import SecurityAgent
from utils.report_generator import generate_natural_language_report

# Configure logging for production
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)

# Load environment variables securely
from dotenv import load_dotenv

load_dotenv()

limiter = Limiter(key_func=get_remote_address, default_limits=["10/minute"])

app = FastAPI(
    title="FastAPI Security Agent",
    description="AI-powered vulnerability detection for FastAPI PRs",
    version="1.0.0",
)

app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

templates = Jinja2Templates(directory="templates")

# Custom exception handlers
@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    return JSONResponse(
        status_code=exc.status_code,
        content={"error": exc.detail, "type": "http_exception"},
    )

@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    logger.error(f"Unhandled exception: {str(exc)}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={"error": "Internal server error", "type": "server_error"},
    )


# Instantiate dependencies
ai_client = GradientAIClient(api_key=config.gradient_api_key)
security_agent = SecurityAgent(ai_client=ai_client, github_token=config.github_token)


@app.get("/")
async def root():
    """Root endpoint with API info."""
    return {
        "message": "FastAPI Security Agent is running",
        "version": "1.0.0",
        "endpoints": {
            "/analyze": "Analyze a single PR",
            "/scan": "Batch analyze multiple PRs",
            "/report": "Generate security report summary",
            "/health": "Health check",
            "/ui": "Web interface"
        }
    }

@app.get("/ui")
async def ui_home(request: Request):
    """Render the web interface."""
    return templates.TemplateResponse("index.html", {"request": request, "result": None})

@app.post("/ui/analyze")
async def ui_analyze(request: Request, pr_url: str = Form(...)):
    """Handle UI form submission for PR analysis."""
    try:
        report = await security_agent.analyze_pull_request(pr_url)
        return templates.TemplateResponse("index.html", {"request": request, "result": report.dict()})
    except Exception as e:
        return templates.TemplateResponse("index.html", {"request": request, "result": {"error": str(e)}})

@app.get("/health")
async def health_check():
    """Health check endpoint for load balancers and monitoring."""
    return {
        "status": "healthy",
        "timestamp": "2025-10-05T12:00:00Z",  # Placeholder; use datetime in prod
        "version": "1.0.0"
    }


@app.post("/analyze", response_model=VulnerabilityReport)
@limiter.limit("5/minute")
async def analyze_pr(request: PRAnalysisRequest, request_obj: Request):
    """
    Analyze a GitHub PR for vulnerabilities.

    This endpoint adapts the Magnet POC for smaller datasets and adds
    error handling for production use.
    """
    try:
        logger.info(f"Analyzing PR: {request.url}")
        report = await security_agent.analyze_pull_request(request.url)
        return report
    except Exception as e:
        logger.error(f"Error analyzing PR {request.url}: {str(e)}")
        raise HTTPException(status_code=500, detail="Analysis failed")


@app.post("/scan")
@limiter.limit("2/minute")
async def scan_multiple_prs(request_obj: Request, urls: List[str]):
    """Batch analyze multiple PRs with concurrency."""
    from asyncio import gather, Semaphore

    semaphore = Semaphore(5)  # Limit concurrent requests
    limited_urls = urls[:30]  # Limit total PRs

    async def analyze_limited(url: str):
        async with semaphore:
            return await security_agent.analyze_pull_request(url)

    results = await gather(*[analyze_limited(url) for url in limited_urls], return_exceptions=True)
    return {
        "results": [
            {
                "url": url,
                "report": result.dict() if not isinstance(result, Exception) else {"error": str(result)},
            }
            for url, result in zip(limited_urls, results)
        ]
    }

@app.get("/report")
async def get_security_report(pr_url: str | None = None):
    """Generate a security report summary. If PR URL provided, analyze it."""
    if pr_url:
        report = await security_agent.analyze_pull_request(pr_url)
        return {
            "type": "detailed",
            "pr_url": pr_url,
            "report": report.dict(),
            "generated_at": "2025-10-05T12:00:00Z"  # Placeholder
        }
    else:
        # Demo summary report
        return {
            "type": "summary",
            "total_analyses": 42,  # Placeholder
            "vulnerabilities_found": 15,
            "most_common": ["sql_injection", "hardcoded_secret"],
            "average_risk_score": 0.65,
            "recommendations": [
                "Implement parameterized queries",
                "Use environment variables for secrets",
                "Add authentication to endpoints"
            ],
            "generated_at": "2025-10-05T12:00:00Z"
        }


if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info",
    )
