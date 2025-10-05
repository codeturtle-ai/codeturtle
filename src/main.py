"""
FastAPI Security Agent - Main application entry point.

This module adapts the existing Magnet POC for smaller-scale analysis
(20-30 PRs) with enhanced error handling and AI integration.
"""

import asyncio
import logging
from typing import List, Optional

import uvicorn
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

# Local modules
from schemas.models import PRAnalysisRequest, VulnerabilityReport
from schemas.config import config
from clients.gradient_ai import GradientAIClient
from ai.agent import SecurityAgent

# Configure logging for production
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)

# Load environment variables securely
from dotenv import load_dotenv

load_dotenv()

app = FastAPI(
    title="FastAPI Security Agent",
    description="AI-powered vulnerability detection for FastAPI PRs",
    version="1.0.0",
)


# Instantiate dependencies
ai_client = GradientAIClient(api_key=config.gradient_api_key)
security_agent = SecurityAgent(ai_client=ai_client)


@app.get("/")
async def root():
    """Health check endpoint."""
    return {"message": "FastAPI Security Agent is running"}


@app.post("/analyze", response_model=VulnerabilityReport)
async def analyze_pr(request: PRAnalysisRequest):
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
async def scan_multiple_prs(urls: List[str]):
    """Batch analyze multiple PRs."""
    # TODO: Implement batch processing with concurrency limits
    results = []
    for url in urls[:30]:  # Limit for performance
        # Placeholder for actual analysis
        results.append({"url": url, "status": "analyzed"})
    return {"results": results}


if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info",
    )
