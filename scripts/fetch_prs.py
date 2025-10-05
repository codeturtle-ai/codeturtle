import requests
import json
import os

# Fetch recent PRs from FastAPI repo
def fetch_fastapi_prs(limit=50):
    url = 'https://api.github.com/repos/tiangolo/fastapi/pulls'
    params = {
        'state': 'closed',  # Include merged PRs
        'per_page': min(limit, 100),
        'page': 1
    }
    
    headers = {}
    token = os.getenv('GITHUB_TOKEN')
    if token:
        headers['Authorization'] = f'Bearer {token}'
    
    response = requests.get(url, params=params, headers=headers)
    response.raise_for_status()
    
    prs = response.json()
    pr_urls = [pr['html_url'] for pr in prs[:limit]]
    
    return pr_urls

if __name__ == '__main__':
    prs = fetch_fastapi_prs(40)  # Get 40 PRs
    with open('data/sample_prs.json', 'w') as f:
        json.dump(prs, f, indent=2)
    print(f'Collected {len(prs)} PR URLs')
