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
security_agent = SecurityAgent(ai_client=ai_client, github_token=config.github_token)


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


if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info",
    )
