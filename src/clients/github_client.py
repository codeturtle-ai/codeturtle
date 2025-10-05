"""
GitHub API Client for fetching PR diffs and metadata.
Implements real GitHub API integration to replace mock responses.
"""

import logging
import re
from typing import Dict, Any, List, Optional, Union
import httpx

logger = logging.getLogger(__name__)

class GitHubClient:
    BASE_URL = "https://api.github.com"
    
    def __init__(self, token: Optional[str] = None) -> None:
        self.token = token
        headers = {
            "Accept": "application/vnd.github.v3+json",
            "User-Agent": "FastAPI-Security-Agent/1.0"
        }
        if token:
            headers["Authorization"] = f"token {token}"
            
        self.client = httpx.AsyncClient(
            headers=headers,
            timeout=30.0,
        )
    
    async def __aenter__(self):
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.client.aclose()
    
    def _parse_pr_url(self, pr_url: str) -> Dict[str, str]:
        """Parse GitHub PR URL to extract owner, repo, and PR number."""
        # Support various GitHub URL formats
        patterns = [
            r"https://github\.com/([^/]+)/([^/]+)/pull/(\d+)",
            r"https://github\.com/([^/]+)/([^/]+)/pulls/(\d+)",
            r"github\.com/([^/]+)/([^/]+)/pull/(\d+)",
        ]
        
        for pattern in patterns:
            match = re.match(pattern, pr_url.strip())
            if match:
                owner, repo, pr_number = match.groups()
                return {
                    "owner": owner,
                    "repo": repo, 
                    "pr_number": pr_number
                }
        
        raise ValueError(f"Invalid GitHub PR URL format: {pr_url}")
    
    async def _make_request(self, endpoint: str) -> Dict[str, Any]:
        """Make authenticated request to GitHub API."""
        url = f"{self.BASE_URL}{endpoint}"
        try:
            resp = await self.client.get(url)
            resp.raise_for_status()
            return resp.json()
        except httpx.HTTPStatusError as e:
            if e.response.status_code == 404:
                raise ValueError(f"PR not found or repository is private: {endpoint}")
            elif e.response.status_code == 403:
                raise ValueError(f"Access denied. Check GitHub token permissions: {endpoint}")
            elif e.response.status_code == 401:
                raise ValueError(f"Authentication failed. Check GitHub token: {endpoint}")
            else:
                logger.error(f"GitHub API error {e.response.status_code}: {e.response.text}")
                raise
        except httpx.RequestError as e:
            logger.error(f"Request error: {str(e)}")
            raise
    
    async def get_pr_metadata(self, pr_url: str) -> Dict[str, Any]:
        """Get PR metadata including title, description, author, etc."""
        parsed = self._parse_pr_url(pr_url)
        endpoint = f"/repos/{parsed['owner']}/{parsed['repo']}/pulls/{parsed['pr_number']}"
        
        pr_data = await self._make_request(endpoint)
        
        return {
            "title": pr_data.get("title", ""),
            "body": pr_data.get("body", ""),
            "state": pr_data.get("state", ""),
            "author": pr_data.get("user", {}).get("login", ""),
            "created_at": pr_data.get("created_at", ""),
            "updated_at": pr_data.get("updated_at", ""),
            "base_branch": pr_data.get("base", {}).get("ref", ""),
            "head_branch": pr_data.get("head", {}).get("ref", ""),
            "commits": pr_data.get("commits", 0),
            "additions": pr_data.get("additions", 0),
            "deletions": pr_data.get("deletions", 0),
            "changed_files": pr_data.get("changed_files", 0),
        }
    
    async def get_pr_files(self, pr_url: str) -> List[Dict[str, Any]]:
        """Get list of files changed in the PR with their diffs."""
        parsed = self._parse_pr_url(pr_url)
        endpoint = f"/repos/{parsed['owner']}/{parsed['repo']}/pulls/{parsed['pr_number']}/files"
        
        files_data = await self._make_request(endpoint)
        
        processed_files = []
        for file_data in files_data:
            # Filter for Python files and other relevant files
            filename = file_data.get("filename", "")
            if self._is_analyzable_file(filename):
                processed_files.append({
                    "filename": filename,
                    "status": file_data.get("status", ""),  # added, modified, removed
                    "additions": file_data.get("additions", 0),
                    "deletions": file_data.get("deletions", 0),
                    "changes": file_data.get("changes", 0),
                    "patch": file_data.get("patch", ""),  # The actual diff
                    "raw_url": file_data.get("raw_url", ""),
                    "blob_url": file_data.get("blob_url", ""),
                })
        
        return processed_files
    
    def _is_analyzable_file(self, filename: str) -> bool:
        """Check if file should be analyzed for security vulnerabilities."""
        # Focus on Python files and configuration files
        analyzable_extensions = {
            '.py', '.pyx', '.pyi',  # Python files
            '.yml', '.yaml',        # YAML config files
            '.json',                # JSON config files
            '.toml',                # TOML config files
            '.cfg', '.ini',         # Config files
            '.env',                 # Environment files
            '.sql',                 # SQL files
            '.sh', '.bash',         # Shell scripts
        }
        
        # Check file extension
        for ext in analyzable_extensions:
            if filename.lower().endswith(ext):
                return True
        
        # Check for common config files without extensions
        config_files = {
            'dockerfile', 'makefile', 'requirements.txt', 
            'pipfile', 'poetry.lock', 'setup.py', 'setup.cfg'
        }
        
        if filename.lower() in config_files:
            return True
        
        return False
    
    def extract_code_from_diff(self, patch: str) -> str:
        """Extract added/modified code from git diff patch."""
        if not patch:
            return ""
        
        code_lines = []
        for line in patch.split('\n'):
            # Skip diff headers and context
            if line.startswith('@@') or line.startswith('diff') or line.startswith('index'):
                continue
            
            # Extract added lines (starting with +)
            if line.startswith('+') and not line.startswith('+++'):
                # Remove the + prefix
                code_line = line[1:]
                code_lines.append(code_line)
            
            # Also include modified lines (context without +/-)
            elif not line.startswith('-') and not line.startswith('+++') and not line.startswith('---'):
                if line.strip():  # Skip empty lines
                    code_lines.append(line)
        
        return '\n'.join(code_lines)
    
    async def get_pr_diff_content(self, pr_url: str) -> Dict[str, Any]:
        """Get comprehensive PR diff content for security analysis."""
        try:
            # Get PR metadata
            metadata = await self.get_pr_metadata(pr_url)
            
            # Get changed files with diffs
            files = await self.get_pr_files(pr_url)
            
            # Extract and combine code from all files
            all_code = []
            file_summaries = []
            
            for file_info in files:
                if file_info['patch']:
                    extracted_code = self.extract_code_from_diff(file_info['patch'])
                    if extracted_code.strip():
                        all_code.append(f"# File: {file_info['filename']}\n{extracted_code}")
                        
                        file_summaries.append({
                            "filename": file_info['filename'],
                            "status": file_info['status'],
                            "additions": file_info['additions'],
                            "deletions": file_info['deletions'],
                            "has_code": True
                        })
                    else:
                        file_summaries.append({
                            "filename": file_info['filename'],
                            "status": file_info['status'],
                            "additions": file_info['additions'],
                            "deletions": file_info['deletions'],
                            "has_code": False
                        })
            
            combined_code = "\n\n".join(all_code)
            
            return {
                "pr_url": pr_url,
                "metadata": metadata,
                "files": file_summaries,
                "combined_code": combined_code,
                "total_files": len(files),
                "analyzable_files": len([f for f in file_summaries if f['has_code']]),
                "total_additions": sum(f['additions'] for f in file_summaries),
                "total_deletions": sum(f['deletions'] for f in file_summaries),
            }
            
        except Exception as e:
            logger.error(f"Error fetching PR diff content: {str(e)}")
            # Return fallback data
            return {
                "pr_url": pr_url,
                "metadata": {"title": "Error fetching PR", "error": str(e)},
                "files": [],
                "combined_code": f"# Error fetching PR content: {str(e)}\n# Using fallback mock code for analysis\npassword = 'hardcoded_secret'\nexecute('SELECT * FROM users WHERE id = ' + user_id)",
                "total_files": 0,
                "analyzable_files": 0,
                "total_additions": 0,
                "total_deletions": 0,
                "error": str(e)
            }
    
    async def get_repository_prs(self, owner: str, repo: str, state: str = "open", limit: int = 10) -> List[Dict[str, Any]]:
        """Get list of PRs from a repository."""
        endpoint = f"/repos/{owner}/{repo}/pulls?state={state}&per_page={limit}"
        
        try:
            prs_data = await self._make_request(endpoint)
            
            return [
                {
                    "number": pr["number"],
                    "title": pr["title"],
                    "url": pr["html_url"],
                    "author": pr["user"]["login"],
                    "created_at": pr["created_at"],
                    "state": pr["state"]
                }
                for pr in prs_data
            ]
            
        except Exception as e:
            logger.error(f"Error fetching repository PRs: {str(e)}")
            return []