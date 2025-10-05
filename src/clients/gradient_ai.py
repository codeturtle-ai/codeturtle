from __future__ import annotations
import logging
import re
from typing import Dict, Any, List, Optional
import httpx
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type

logger = logging.getLogger(__name__)

class GradientAIClient:
    # Real DigitalOcean API endpoints
    BASE_URL = "https://api.digitalocean.com/v2/ai"
    MODELS_ENDPOINT = "/models"
    COMPLETIONS_ENDPOINT = "/completions"
    
    def __init__(self, api_key: Optional[str]) -> None:
        self.api_key = api_key
        self.client = httpx.AsyncClient(
            headers={
                "Authorization": f"Bearer {api_key}" if api_key else {},
                "Content-Type": "application/json"
            },
            timeout=60.0,  # Increased timeout for AI processing
        )
        # Use a general-purpose model for code analysis
        self.model = "gpt-3.5-turbo"  # Fallback model

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

    def _create_security_prompt(self, code_snippet: str) -> str:
        """Create a specialized prompt for security analysis."""
        return f"""You are a security expert analyzing code for vulnerabilities. 
        
Analyze this code snippet for security vulnerabilities:

```python
{code_snippet}
```

Focus on these vulnerability types:
1. SQL Injection (raw queries, string concatenation)
2. Server-Side Template Injection (eval, exec, unsafe templating)
3. Hardcoded Secrets (API keys, passwords, tokens)
4. Missing Authentication (unprotected endpoints)
5. Insecure Deserialization (pickle, yaml.load)
6. Path Traversal (file operations with user input)
7. Command Injection (subprocess with user input)

Respond in JSON format:
{{
    "vulnerabilities": ["list of vulnerability types found"],
    "confidence": 0.0-1.0,
    "severity": "low|medium|high|critical",
    "findings": [
        {{
            "type": "vulnerability_type",
            "line": "line_number_if_applicable", 
            "description": "detailed explanation",
            "recommendation": "specific fix suggestion"
        }}
    ],
    "recommendations": ["list of general security recommendations"]
}}"""

    def _parse_ai_response(self, response_text: str) -> Dict[str, Any]:
        """Parse AI response and extract structured data."""
        try:
            # Try to extract JSON from the response
            import json
            
            # Look for JSON block in response
            json_match = re.search(r'\{[^{}]*(?:\{[^{}]*\}[^{}]*)*\}', response_text, re.DOTALL)
            if json_match:
                json_str = json_match.group()
                parsed = json.loads(json_str)
                return parsed
            
            # Fallback: parse response manually
            vulnerabilities = []
            confidence = 0.5
            recommendations = []
            
            # Extract vulnerabilities mentioned
            vuln_patterns = {
                'sql injection': ['sql', 'injection', 'query', 'database'],
                'ssti': ['template', 'eval', 'exec', 'injection'],
                'hardcoded_secret': ['password', 'key', 'token', 'secret'],
                'missing_auth': ['auth', 'authentication', 'unauthorized'],
                'insecure_deserialization': ['pickle', 'yaml', 'deserial'],
                'path_traversal': ['path', 'file', 'directory', 'traversal'],
                'command_injection': ['command', 'subprocess', 'shell']
            }
            
            response_lower = response_text.lower()
            for vuln_type, keywords in vuln_patterns.items():
                if any(keyword in response_lower for keyword in keywords):
                    vulnerabilities.append(vuln_type)
            
            # Extract confidence if mentioned
            conf_match = re.search(r'confidence["\s:]*([0-9.]+)', response_lower)
            if conf_match:
                confidence = float(conf_match.group(1))
                if confidence > 1.0:
                    confidence = confidence / 100.0  # Convert percentage
            
            # Extract recommendations
            if 'recommend' in response_lower:
                rec_lines = [line.strip() for line in response_text.split('\n') 
                           if 'recommend' in line.lower() or line.strip().startswith('-')]
                recommendations = rec_lines[:3]  # Limit to 3
            
            return {
                "vulnerabilities": vulnerabilities,
                "confidence": confidence,
                "recommendations": recommendations or ["Review code for security best practices"]
            }
            
        except Exception as e:
            logger.error(f"Error parsing AI response: {e}")
            return {
                "vulnerabilities": ["parsing_error"],
                "confidence": 0.0,
                "recommendations": ["Unable to parse AI response"]
            }

    async def analyze_code(self, code_snippet: str) -> Dict[str, Any]:
        """Analyze code for vulnerabilities using DigitalOcean AI."""
        if not self.api_key:
            logger.warning("No API key provided; using enhanced fallback analysis")
            return self._enhanced_fallback_analysis(code_snippet)

        # Create security-focused prompt
        prompt = self._create_security_prompt(code_snippet)
        
        payload = {
            "model": self.model,
            "messages": [
                {
                    "role": "system",
                    "content": "You are a cybersecurity expert specializing in code vulnerability analysis."
                },
                {
                    "role": "user", 
                    "content": prompt
                }
            ],
            "max_tokens": 1000,
            "temperature": 0.1  # Low temperature for consistent security analysis
        }

        try:
            result = await self._make_request(self.COMPLETIONS_ENDPOINT, payload)
            
            # Extract response text
            response_text = ""
            if "choices" in result and len(result["choices"]) > 0:
                response_text = result["choices"][0].get("message", {}).get("content", "")
            
            # Parse the AI response
            parsed_result = self._parse_ai_response(response_text)
            
            # Normalize the response format
            return {
                "labels": parsed_result.get("vulnerabilities", []),
                "confidence": parsed_result.get("confidence", 0.0),
                "recommendations": parsed_result.get("recommendations", []),
                "raw_response": response_text[:500]  # Keep first 500 chars for debugging
            }
            
        except Exception as e:
            logger.error(f"Error analyzing code with AI: {str(e)}")
            # Enhanced fallback analysis
            return self._enhanced_fallback_analysis(code_snippet)
    
    def _enhanced_fallback_analysis(self, code_snippet: str) -> Dict[str, Any]:
        """Enhanced fallback analysis when AI is unavailable."""
        vulnerabilities = []
        confidence = 0.0
        recommendations = []
        
        code_lower = code_snippet.lower()
        
        # Pattern-based detection
        patterns = {
            'sql_injection': {
                'patterns': ['select ', 'insert ', 'update ', 'delete ', 'drop ', 'execute(', 'executemany('],
                'confidence': 0.7,
                'recommendation': 'Use parameterized queries or ORM methods'
            },
            'ssti': {
                'patterns': ['eval(', 'exec(', 'compile(', 'render_template_string'],
                'confidence': 0.9,
                'recommendation': 'Avoid eval/exec and use safe templating'
            },
            'hardcoded_secret': {
                'patterns': ['password=', 'api_key=', 'secret=', 'token=', 'key="', "key='"],
                'confidence': 0.6,
                'recommendation': 'Use environment variables for secrets'
            },
            'command_injection': {
                'patterns': ['subprocess.', 'os.system(', 'os.popen(', 'shell=true'],
                'confidence': 0.8,
                'recommendation': 'Validate input and avoid shell=True'
            },
            'insecure_deserialization': {
                'patterns': ['pickle.load', 'yaml.load', 'marshal.load'],
                'confidence': 0.8,
                'recommendation': 'Use safe deserialization methods'
            }
        }
        
        for vuln_type, config in patterns.items():
            if any(pattern in code_lower for pattern in config['patterns']):
                vulnerabilities.append(vuln_type)
                confidence = max(confidence, config['confidence'])
                recommendations.append(config['recommendation'])
        
        # If no vulnerabilities found, still provide some confidence
        if not vulnerabilities:
            confidence = 0.3  # Low confidence that code is safe
            recommendations = ['Code appears safe, but manual review recommended']
        
        return {
            "labels": vulnerabilities,
            "confidence": confidence,
            "recommendations": list(set(recommendations)),  # Remove duplicates
            "analysis_method": "fallback_pattern_matching"
        }
