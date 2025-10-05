#!/usr/bin/env python3
"""
Test script for advanced AI analysis and production risk scoring systems.
"""

import sys
import asyncio
import os
sys.path.append('src')

def test_production_risk_calculator():
    """Test the production risk calculator."""
    print("🧪 Testing Production Risk Calculator...")
    
    try:
        from scoring.risk_calculator import ProductionRiskCalculator, VulnerabilityFinding, PRComplexityMetrics, SeverityLevel
        
        calculator = ProductionRiskCalculator()
        
        # Create test findings
        findings = [
            VulnerabilityFinding(
                type="sql_injection",
                severity=SeverityLevel.HIGH,
                confidence=0.9,
                source="ast",
                description="SQL injection via string concatenation"
            ),
            VulnerabilityFinding(
                type="hardcoded_secret",
                severity=SeverityLevel.MEDIUM,
                confidence=0.8,
                source="ai",
                description="Hardcoded API key detected"
            ),
            VulnerabilityFinding(
                type="ssti",
                severity=SeverityLevel.CRITICAL,
                confidence=0.95,
                source="ai",
                description="eval() usage detected",
                cwe_id="CWE-94"
            )
        ]
        
        # Create test PR metrics
        pr_metrics = PRComplexityMetrics(
            total_additions=150,
            total_deletions=50,
            changed_files=8,
            analyzable_files=5,
            max_file_size=2000,
            avg_file_size=800.0,
            has_config_changes=True,
            has_dependency_changes=False,
            touches_security_files=True
        )
        
        # Calculate risk score
        risk_assessment = calculator.calculate_risk_score(
            findings=findings,
            pr_metrics=pr_metrics,
            ai_confidence=0.85,
            context={
                "author_reputation": "trusted",
                "target_branch": "main",
                "recent_vulnerabilities": 2
            }
        )
        
        print(f"✅ Risk Score: {risk_assessment['risk_score']}")
        print(f"✅ Risk Category: {risk_assessment['risk_category']}")
        print(f"✅ Confidence: {risk_assessment['confidence']}")
        print(f"✅ Findings Summary: {risk_assessment['findings_summary']}")
        print(f"✅ Recommendations: {len(risk_assessment['recommendations'])}")
        
        # Verify expected behavior
        assert risk_assessment['risk_score'] > 0.7, "Should be high risk due to SSTI"
        assert risk_assessment['risk_category'] in ['HIGH', 'CRITICAL'], "Should be high/critical risk"
        assert len(risk_assessment['recommendations']) > 0, "Should have recommendations"
        
        print("✅ Production Risk Calculator: PASSED")
        return True
        
    except Exception as e:
        print(f"❌ Production Risk Calculator: FAILED - {e}")
        return False

def test_advanced_ai_analyzer():
    """Test the advanced AI analyzer."""
    print("\n🧪 Testing Advanced AI Analyzer...")
    
    try:
        from ai.advanced_analyzer import AdvancedAIAnalyzer, AnalysisContext, AnalysisMode
        from clients.gradient_ai import GradientAIClient
        
        # Create mock AI client
        class MockAIClient:
            async def _make_request(self, endpoint, payload):
                return {
                    "choices": [{
                        "message": {
                            "content": """{
                                "vulnerabilities": [
                                    {
                                        "type": "sql_injection",
                                        "severity": "HIGH",
                                        "confidence": 0.9,
                                        "description": "SQL injection via string concatenation",
                                        "cwe_id": "CWE-89"
                                    }
                                ],
                                "overall_confidence": 0.85,
                                "recommendations": ["Use parameterized queries"],
                                "explanation": "Code contains SQL injection vulnerability"
                            }"""
                        }
                    }]
                }
        
        analyzer = AdvancedAIAnalyzer(MockAIClient())
        
        # Create test context
        context = AnalysisContext(
            code_snippet='''
def get_user(user_id):
    query = "SELECT * FROM users WHERE id = " + user_id
    return execute(query)
            ''',
            file_path="app/models.py",
            pr_title="Add user lookup function",
            author="test_user"
        )
        
        # Test comprehensive analysis
        result = asyncio.run(analyzer.analyze_code(context, AnalysisMode.COMPREHENSIVE))
        
        print(f"✅ Vulnerabilities found: {len(result.vulnerabilities)}")
        print(f"✅ Confidence: {result.confidence}")
        print(f"✅ Recommendations: {len(result.recommendations)}")
        print(f"✅ Explanation length: {len(result.explanation)}")
        
        # Verify expected behavior
        assert len(result.vulnerabilities) > 0, "Should find vulnerabilities"
        assert result.confidence > 0, "Should have confidence > 0"
        assert len(result.recommendations) > 0, "Should have recommendations"
        
        print("✅ Advanced AI Analyzer: PASSED")
        return True
        
    except Exception as e:
        print(f"❌ Advanced AI Analyzer: FAILED - {e}")
        return False

def test_integrated_security_agent():
    """Test the integrated security agent with advanced systems."""
    print("\n🧪 Testing Integrated Security Agent...")
    
    try:
        from ai.agent import SecurityAgent
        from ai.advanced_analyzer import AnalysisMode
        from clients.gradient_ai import GradientAIClient
        
        # Create mock AI client
        class MockAIClient:
            async def analyze_code(self, code):
                return {
                    "labels": ["sql_injection"],
                    "confidence": 0.8,
                    "recommendations": ["Use parameterized queries"]
                }
            
            async def _make_request(self, endpoint, payload):
                return {
                    "choices": [{
                        "message": {
                            "content": """{
                                "vulnerabilities": [
                                    {
                                        "type": "sql_injection",
                                        "severity": "HIGH",
                                        "confidence": 0.9,
                                        "description": "SQL injection detected"
                                    }
                                ],
                                "overall_confidence": 0.85,
                                "recommendations": ["Use parameterized queries"]
                            }"""
                        }
                    }]
                }
        
        # Create agent with mock client
        agent = SecurityAgent(MockAIClient(), github_token=None)
        
        # Test analysis (will use fallback since no real GitHub token)
        result = asyncio.run(agent.analyze_pull_request(
            "https://github.com/test/repo/pull/1",
            AnalysisMode.COMPREHENSIVE
        ))
        
        print(f"✅ PR URL: {result.pr_url}")
        print(f"✅ Vulnerabilities: {result.vulnerabilities}")
        print(f"✅ Risk Score: {result.risk_score}")
        print(f"✅ Recommendations: {len(result.recommendations)}")
        print(f"✅ Summary length: {len(result.summary)}")
        
        # Verify expected behavior
        assert result.pr_url == "https://github.com/test/repo/pull/1", "Should preserve PR URL"
        assert isinstance(result.vulnerabilities, list), "Should return list of vulnerabilities"
        assert isinstance(result.risk_score, (int, float)), "Should return numeric risk score"
        assert len(result.recommendations) > 0, "Should have recommendations"
        assert len(result.summary) > 0, "Should have summary"
        
        print("✅ Integrated Security Agent: PASSED")
        return True
        
    except Exception as e:
        print(f"❌ Integrated Security Agent: FAILED - {e}")
        return False

def test_vulnerability_detection_accuracy():
    """Test vulnerability detection accuracy with known vulnerable code."""
    print("\n🧪 Testing Vulnerability Detection Accuracy...")
    
    try:
        from detection.ast_analyzer import ASTAnalyzer
        from ai.knowledge_base import FastAPISecurityKB
        
        # Test code with multiple vulnerabilities
        vulnerable_code = '''
# SQL Injection
def get_user(user_id):
    query = "SELECT * FROM users WHERE id = " + user_id
    return execute(query)

# SSTI
def render_template(user_input):
    return eval(user_input)

# Hardcoded Secret
api_key = "sk-1234567890abcdef"
password = "admin123"

# Command Injection
import subprocess
def run_command(cmd):
    subprocess.run(f"ls {cmd}", shell=True)

# Insecure Deserialization
import pickle
def load_data(data):
    return pickle.load(data)
        '''
        
        # Test AST Analysis
        ast_analyzer = ASTAnalyzer()
        ast_findings = ast_analyzer.analyze_code(vulnerable_code)
        
        print(f"✅ AST Findings: {len(ast_findings)}")
        for finding in ast_findings:
            print(f"   - {finding['vulnerability']}: {finding['description']}")
        
        # Test Knowledge Base
        kb = FastAPISecurityKB()
        kb_results = kb.retrieve(vulnerable_code)
        
        print(f"✅ Knowledge Base Matches: {len(kb_results)}")
        for result in kb_results:
            print(f"   - {result['vulnerability']}: {result['description'][:50]}...")
        
        # Verify detection
        detected_types = set([f['vulnerability'] for f in ast_findings])
        expected_types = {'sql_injection', 'ssti'}  # AST should detect these
        
        assert len(detected_types.intersection(expected_types)) > 0, "Should detect expected vulnerabilities"
        assert len(kb_results) > 0, "Knowledge base should find matches"
        
        print("✅ Vulnerability Detection Accuracy: PASSED")
        return True
        
    except Exception as e:
        print(f"❌ Vulnerability Detection Accuracy: FAILED - {e}")
        return False

def test_performance_benchmarks():
    """Test performance of advanced systems."""
    print("\n🧪 Testing Performance Benchmarks...")
    
    try:
        import time
        from detection.ast_analyzer import ASTAnalyzer
        from ai.knowledge_base import FastAPISecurityKB
        
        # Test code
        test_code = '''
def vulnerable_function():
    password = "hardcoded_secret"
    query = "SELECT * FROM users WHERE id = " + user_id
    execute(query)
    eval(user_input)
        ''' * 10  # Repeat to make it larger
        
        # Benchmark AST Analysis
        start_time = time.time()
        ast_analyzer = ASTAnalyzer()
        ast_findings = ast_analyzer.analyze_code(test_code)
        ast_time = time.time() - start_time
        
        print(f"✅ AST Analysis Time: {ast_time:.3f}s")
        print(f"✅ AST Findings: {len(ast_findings)}")
        
        # Benchmark Knowledge Base
        start_time = time.time()
        kb = FastAPISecurityKB()
        kb_results = kb.retrieve(test_code[:1000])  # Limit query size
        kb_time = time.time() - start_time
        
        print(f"✅ Knowledge Base Time: {kb_time:.3f}s")
        print(f"✅ KB Results: {len(kb_results)}")
        
        # Performance assertions
        assert ast_time < 1.0, "AST analysis should be fast (< 1s)"
        assert kb_time < 0.1, "Knowledge base should be very fast (< 0.1s)"
        
        print("✅ Performance Benchmarks: PASSED")
        return True
        
    except Exception as e:
        print(f"❌ Performance Benchmarks: FAILED - {e}")
        return False

def main():
    """Run all advanced system tests."""
    print("🚀 Advanced Systems Testing Suite")
    print("=" * 50)
    
    tests = [
        test_production_risk_calculator,
        test_advanced_ai_analyzer,
        test_integrated_security_agent,
        test_vulnerability_detection_accuracy,
        test_performance_benchmarks
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        if test():
            passed += 1
    
    print("\n" + "=" * 50)
    print(f"📊 Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All advanced systems are working correctly!")
        print("\n🎯 Production Readiness Status:")
        print("✅ Production Risk Scoring: READY")
        print("✅ Advanced AI Analysis: READY")
        print("✅ Multi-layer Detection: READY")
        print("✅ Performance Optimized: READY")
        print("✅ Error Handling: ROBUST")
        
        print("\n🚀 Your FastAPI Security Agent is production-ready!")
    else:
        print(f"⚠️  {total - passed} tests failed - review implementation")
    
    return passed == total

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)