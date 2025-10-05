import asyncio
import json
from src.schemas.models import PRAnalysisRequest
from src.main import app

# Simple sanity test: instantiate request model and ensure fields are intact
req = PRAnalysisRequest(url='https://github.com/example/repo/pull/1')
assert req.url.endswith('/pull/1')
assert 1 <= req.max_prs <= 50
print('OK')
