import os
from pydantic import BaseModel

class AppConfig(BaseModel):
    gradient_api_key: str | None = os.getenv("GRADIENT_AI_API_KEY")
    github_token: str | None = os.getenv("GITHUB_TOKEN")

config = AppConfig()
