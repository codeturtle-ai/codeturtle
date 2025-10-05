import json
import csv
from collections import Counter
import statistics

def analyze_results():
    """Analyze batch analysis results and generate statistics."""
    
    # Load results
    with open('data/analysis_results.json', 'r') as f:
        results = json.load(f)
    
    # Filter successful analyses
    successful_results = [r for r in results if r.get('success', False)]
    
    if not successful_results:
        print('No successful analyses found')
        return
    
    # Basic statistics
    total_analyzed = len(successful_results)
    total_prs = len(results)
    
    # Vulnerability analysis
    all_vulnerabilities = []
    risk_scores = []
    
    for result in successful_results:
        report = result['report']
        all_vulnerabilities.extend(report.get('vulnerabilities', []))
        risk_scores.append(report.get('risk_score', 0))
    
    vuln_counts = Counter(all_vulnerabilities)
    most_common_vulns = vuln_counts.most_common(5)
    
    # Risk score statistics
    avg_risk_score = statistics.mean(risk_scores) if risk_scores else 0
    median_risk = statistics.median(risk_scores) if risk_scores else 0
    high_risk_count = sum(1 for score in risk_scores if score > 0.7)
    
    # Generate statistics report
    stats = {
        'total_prs_analyzed': total_prs,
        'successful_analyses': total_analyzed,
        'success_rate': round(total_analyzed / total_prs * 100, 1),
        'total_vulnerabilities_found': len(all_vulnerabilities),
        'unique_vulnerability_types': len(vuln_counts),
        'most_common_vulnerabilities': most_common_vulns,
        'average_risk_score': round(avg_risk_score, 3),
        'median_risk_score': round(median_risk, 3),
        'high_risk_prs': high_risk_count,
        'risk_score_distribution': {
            'low': sum(1 for s in risk_scores if s < 0.3),
            'medium': sum(1 for s in risk_scores if 0.3 <= s < 0.7),
            'high': sum(1 for s in risk_scores if s >= 0.7)
        }
    }
    
    # Save statistics
    with open('data/analysis_stats.json', 'w') as f:
        json.dump(stats, f, indent=2)
    
    # Print summary
    print('=== Analysis Statistics ===')
    print(f'Total PRs: {total_prs}')
    print(f'Successful analyses: {total_analyzed} ({stats["success_rate"]}%)')
    print(f'Total vulnerabilities found: {stats["total_vulnerabilities_found"]}')
    print(f'Average risk score: {stats["average_risk_score"]}')
    print(f'Most common vulnerabilities: {stats["most_common_vulnerabilities"]}')
    
    return stats

if __name__ == '__main__':
    analyze_results()
