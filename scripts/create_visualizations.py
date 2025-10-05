import json
import matplotlib
matplotlib.use('Agg')  # Use non-interactive backend
import matplotlib.pyplot as plt

def create_visualizations():
    """Create data visualizations from analysis results."""
    
    # Load stats
    with open('data/analysis_stats.json', 'r') as f:
        stats = json.load(f)
    
    # Load raw results for detailed analysis
    with open('data/analysis_results.json', 'r') as f:
        results = json.load(f)
    
    successful_results = [r for r in results if r.get('success', False)]
    
    # 1. Vulnerability Types Pie Chart Data
    vuln_counts = stats['most_common_vulnerabilities']
    vuln_labels = [v[0] for v in vuln_counts]
    vuln_values = [v[1] for v in vuln_counts]
    
    # 2. Risk Score Distribution Bar Chart Data
    risk_dist = stats['risk_score_distribution']
    
    # 3. Risk Score Histogram Data
    risk_scores = [r['report']['risk_score'] for r in successful_results]
    
    # Save chart data as JSON for external plotting
    chart_data = {
        'vulnerability_pie': {
            'labels': vuln_labels,
            'values': vuln_values,
            'title': 'Most Common Vulnerabilities Found'
        },
        'risk_distribution_bar': {
            'labels': list(risk_dist.keys()),
            'values': list(risk_dist.values()),
            'title': 'Risk Score Distribution'
        },
        'risk_histogram': {
            'scores': risk_scores,
            'bins': [0, 0.2, 0.4, 0.6, 0.8, 1.0],
            'title': 'Risk Score Histogram'
        }
    }
    
    with open('data/chart_data.json', 'w') as f:
        json.dump(chart_data, f, indent=2)
    
    # Generate ASCII bar chart for vulnerability counts
    print('\n=== Vulnerability Distribution ===')
    max_count = max(vuln_values) if vuln_values else 1
    for label, count in vuln_counts:
        bar = '█' * int(count / max_count * 20)
        print(f'{label}: {bar} ({count})')
    
    # Generate ASCII histogram for risk scores
    print('\n=== Risk Score Distribution ===')
    bins = [0, 0.2, 0.4, 0.6, 0.8, 1.0]
    hist = [0] * (len(bins) - 1)
    
    for score in risk_scores:
        for i in range(len(bins) - 1):
            if bins[i] <= score < bins[i + 1]:
                hist[i] += 1
                break
        if score == 1.0:
            hist[-1] += 1
    
    max_hist = max(hist) if hist else 1
    for i, count in enumerate(hist):
        bar = '█' * int(count / max_hist * 20)
        print(f'{bins[i]:.1f}-{bins[i+1]:.1f}: {bar} ({count})')
    
    return chart_data

if __name__ == '__main__':
    create_visualizations()
