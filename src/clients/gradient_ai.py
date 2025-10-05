from __future__ import annotations
from typing import List

class GradientAIClient:
    def __init__(self, api_key: str | None) -> None:
        self.api_key = api_key

    async def analyze_code(self, code_snippet: str) -> dict:
        # Placeholder: call to Gradient AI service
        # Return a deterministic shape for downstream consumers
        return {
            "labels": ["sql_injection", "hardcoded_secret"],
            "confidence": 0.82,
            "recommendations": [
                "Use parameterized queries",
                "Move secrets to environment variables",
            ],
        }
