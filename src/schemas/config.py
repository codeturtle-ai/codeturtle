import os
from typing import Optional
from pydantic import BaseModel

class AppConfig(BaseModel):
    gradient_api_key: Optional[str] = os.getenv("GRADIENT_AI_API_KEY")
    github_token: Optional[str] = os.getenv("GITHUB_TOKEN")

config = AppConfig()
