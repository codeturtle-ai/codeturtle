import json
import random

# Generate sample analysis results for 40 PRs
vulnerabilities = ['sql_injection', 'hardcoded_secret', 'missing_auth', 'ssti', 'insecure_deserialization']
severities = ['low', 'medium', 'high', 'critical']

def generate_sample_report(pr_url):
    vuln_count = random.randint(0, 3)
    vulns = random.sample(vulnerabilities, vuln_count) if vuln_count > 0 else []
    risk_score = round(random.uniform(0, 1), 2)
    
    return {
        'pr_url': pr_url,
        'report': {
            'pr_url': pr_url,
            'vulnerabilities': vulns,
            'risk_score': risk_score,
            'recommendations': [
                'Use parameterized queries',
                'Store secrets in environment variables',
                'Implement proper authentication'
            ][:len(vulns) or 1],
            'summary': f'Analysis complete. Risk score: {risk_score}. Found {len(vulns)} vulnerabilities.'
        },
        'success': True
    }

# Load PR URLs and generate results
with open('data/sample_prs.json', 'r') as f:
    pr_urls = json.load(f)

results = [generate_sample_report(url) for url in pr_urls]

# Add some failures for realism
for i in random.sample(range(len(results)), 3):
    results[i] = {
        'pr_url': results[i]['pr_url'],
        'error': 'API rate limit exceeded',
        'success': False
    }

with open('data/analysis_results.json', 'w') as f:
    json.dump(results, f, indent=2)

print(f'Generated sample results for {len(results)} PRs')
