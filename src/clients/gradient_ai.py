from __future__ import annotations
import logging
from typing import Dict, Any
import httpx
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type

logger = logging.getLogger(__name__)

class GradientAIClient:
    BASE_URL = "https://api.digitalocean.com/v2/gradient"  # Placeholder; use actual Gradient AI endpoint

    def __init__(self, api_key: str | None) -> None:
        self.api_key = api_key
        self.client = httpx.AsyncClient(
            headers={"Authorization": f"Bearer {api_key}"} if api_key else {},
            timeout=30.0,
        )

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.client.aclose()

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=4, max=10),
        retry=retry_if_exception_type((httpx.RequestError, httpx.HTTPStatusError)),
    )
    async def _make_request(self, endpoint: str, payload: Dict[str, Any]) -> Dict[str, Any]:
        url = f"{self.BASE_URL}{endpoint}"
        try:
            resp = await self.client.post(url, json=payload)
            resp.raise_for_status()
            return resp.json()
        except httpx.HTTPStatusError as e:
            logger.error(f"HTTP error {e.response.status_code}: {e.response.text}")
            raise
        except httpx.RequestError as e:
            logger.error(f"Request error: {str(e)}")
            raise

    async def analyze_code(self, code_snippet: str) -> Dict[str, Any]:
        """Analyze code for vulnerabilities using Gradient AI."""
        if not self.api_key:
            logger.warning("No API key provided; returning mock response")
            return {
                "labels": ["sql_injection", "hardcoded_secret"],
                "confidence": 0.82,
                "recommendations": [
                    "Use parameterized queries",
                    "Move secrets to environment variables",
                ],
            }

        payload = {
            "input": code_snippet,
            "task": "vulnerability_detection",  # Hypothetical task
        }

        try:
            result = await self._make_request("/infer", payload)
            # Parse and normalize response (adjust based on actual API)
            return {
                "labels": result.get("vulnerabilities", []),
                "confidence": result.get("confidence", 0.0),
                "recommendations": result.get("recommendations", []),
            }
        except Exception as e:
            logger.error(f"Error analyzing code: {str(e)}")
            # Fallback to mock
            return {
                "labels": ["analysis_failed"],
                "confidence": 0.0,
                "recommendations": ["Check API configuration"],
            }
