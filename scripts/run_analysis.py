import asyncio
import json
import os
import sys
import logging
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / 'src'))

from clients.gradient_ai import GradientAIClient
from ai.agent import SecurityAgent

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def run_batch_analysis():
    """Run batch analysis on collected PRs."""
    # Load PR URLs
    with open('data/sample_prs.json', 'r') as f:
        pr_urls = json.load(f)
    
    logger.info(f'Starting analysis of {len(pr_urls)} PRs...')
    
    # Initialize agent
    api_key = os.getenv('GRADIENT_AI_API_KEY')
    github_token = os.getenv('GITHUB_TOKEN')
    
    ai_client = GradientAIClient(api_key=api_key)
    agent = SecurityAgent(ai_client=ai_client, github_token=github_token)
    
    results = []
    
    # Process in batches to avoid overwhelming APIs
    batch_size = 5
    for i in range(0, len(pr_urls), batch_size):
        batch = pr_urls[i:i+batch_size]
        logger.info(f'Processing batch {i//batch_size + 1}: PRs {i+1}-{min(i+batch_size, len(pr_urls))}')
        
        batch_results = []
        for pr_url in batch:
            try:
                report = await agent.analyze_pull_request(pr_url)
                batch_results.append({
                    'pr_url': pr_url,
                    'report': report.dict(),
                    'success': True
                })
                logger.info(f'✓ Analyzed {pr_url}')
            except Exception as e:
                logger.error(f'✗ Failed to analyze {pr_url}: {str(e)}')
                batch_results.append({
                    'pr_url': pr_url,
                    'error': str(e),
                    'success': False
                })
        
        results.extend(batch_results)
        
        # Small delay between batches
        await asyncio.sleep(1)
    
    # Save results
    with open('data/analysis_results.json', 'w') as f:
        json.dump(results, f, indent=2)
    
    successful = sum(1 for r in results if r.get('success', False))
    logger.info(f'Analysis complete: {successful}/{len(results)} successful')
    
    return results

if __name__ == '__main__':
    asyncio.run(run_batch_analysis())
