from typing import List

def generate_natural_language_report(vulnerabilities: List[str], risk_score: float, recommendations: List[str]) -> str:
    """Generate a human-readable vulnerability report."""
    vuln_count = len([v for v in vulnerabilities if v != "analysis_error"])
    
    if vuln_count == 0:
        return f"Security Analysis Complete: No significant vulnerabilities detected (Risk Score: {risk_score:.2f}). The code appears secure based on current analysis."
    
    vuln_summary = f"Detected {vuln_count} potential vulnerability type(s): {', '.join(vulnerabilities[:3])}{'...' if len(vulnerabilities) > 3 else ''}."
    risk_desc = f"Overall Risk Score: {risk_score:.2f} (" + (
        "Low" if risk_score < 0.3 else "Medium" if risk_score < 0.7 else "High" if risk_score < 0.9 else "Critical"
    ) + ")."
    
    rec_summary = f"Recommendations: {'; '.join(recommendations[:3])}{'...' if len(recommendations) > 3 else '.'}"
    
    return f"{vuln_summary} {risk_desc} {rec_summary}"
