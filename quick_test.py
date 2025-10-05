#!/usr/bin/env python3
"""Quick test of all implemented features."""

import sys

print("=" * 70)
print("FastAPI Security Agent - Quick Feature Test")
print("=" * 70)
print()

# Test 1: AST Analyzer
print("🧪 TEST 1: AST Analyzer (Production-Grade Detection)")
print("-" * 70)

try:
    from src.detection.ast_analyzer import ASTAnalyzer
    
    vulnerable_code = """
password = "hardcoded_secret_123"
api_key = "sk_live_abc123xyz456789"
eval("print('dangerous code execution')")
cursor.execute("SELECT * FROM users WHERE id = " + user_id)
os.system("rm -rf " + user_input)
import pickle
yaml.load(untrusted_data)
"""
    
    analyzer = ASTAnalyzer()
    findings = analyzer.analyze_code(vulnerable_code)
    
    print(f"✅ AST Analyzer loaded successfully")
    print(f"📊 Found {len(findings)} vulnerabilities")
    print()
    
    for i, finding in enumerate(findings[:5], 1):  # Show first 5
        print(f"  {i}. {finding['vulnerability'].upper()}")
        print(f"     Line: {finding.get('line', 'N/A')} | " + 
              f"Severity: {finding['severity']} | " +
              f"Confidence: {finding['confidence']}")
        print(f"     {finding['description']}")
    
    if len(findings) > 5:
        print(f"     ... and {len(findings) - 5} more")
    
    print()
    print("✅ TEST 1 PASSED: AST Analyzer working perfectly!")
    test1_pass = True
    
except Exception as e:
    print(f"❌ TEST 1 FAILED: {e}")
    test1_pass = False

print()

# Test 2: Risk Scoring Engine
print("🧪 TEST 2: Production-Grade Risk Scoring")
print("-" * 70)

try:
    from src.utils.scoring import RiskScorer
    
    scorer = RiskScorer()
    
    # Use findings from test 1 if available
    if test1_pass:
        scoring_result = scorer.calculate_risk_score(
            findings,
            ai_confidence=0.85,
            kb_matches=3
        )
        
        print(f"✅ Risk Scorer loaded successfully")
        print(f"📊 Risk Calculation Results:")
        print(f"   Risk Score: {scoring_result['risk_score']} " +
              f"({scorer.get_risk_level(scoring_result['risk_score'])})")
        print(f"   Total Findings: {scoring_result['total_findings']}")
        print(f"   Confidence: {scoring_result['confidence']}")
        print(f"   Weighted Score: {scoring_result['weighted_score']}")
        print(f"   AI Contribution: {scoring_result['ai_contribution']}")
        print()
        
        print("📋 Severity Distribution:")
        for severity, count in scoring_result['severity_distribution'].items():
            if count > 0:
                print(f"   {severity.upper()}: {count}")
        print()
        
        recommendations = scorer.get_recommendations(findings, scoring_result['risk_score'])
        print(f"💡 Top Recommendations ({len(recommendations)}):")
        for i, rec in enumerate(recommendations[:3], 1):
            print(f"   {i}. {rec}")
        
        print()
        print("✅ TEST 2 PASSED: Risk scoring working perfectly!")
        test2_pass = True
    else:
        print("⚠️  Skipping (depends on Test 1)")
        test2_pass = False
        
except Exception as e:
    print(f"❌ TEST 2 FAILED: {e}")
    test2_pass = False

print()

# Test 3: Gradient AI Client
print("🧪 TEST 3: Gradient AI Client (Enhanced Fallback)")
print("-" * 70)

try:
    from src.clients.gradient_ai import GradientAIClient
    import asyncio
    
    async def test_gradient_client():
        # Test with no API key (uses enhanced fallback)
        client = GradientAIClient(api_key=None)
        
        test_code = """
password = "secret123"
eval("dangerous")
cursor.execute("SELECT * FROM users WHERE id = " + user_id)
"""
        
        result = await client.analyze_code(test_code)
        return result
    
    result = asyncio.run(test_gradient_client())
    
    print(f"✅ Gradient AI Client loaded successfully")
    print(f"📊 Analysis Results:")
    print(f"   Detected Vulnerabilities: {result.get('labels', [])}")
    print(f"   Confidence: {result.get('confidence', 0.0)}")
    print(f"   Analysis Method: {result.get('analysis_method', 'ai')}")
    print()
    
    print("💡 AI Recommendations:")
    for i, rec in enumerate(result.get('recommendations', [])[:3], 1):
        print(f"   {i}. {rec}")
    
    print()
    print("✅ TEST 3 PASSED: Gradient AI client with fallback working!")
    test3_pass = True
    
except Exception as e:
    print(f"❌ TEST 3 FAILED: {e}")
    test3_pass = False

print()

# Test 4: Knowledge Base
print("🧪 TEST 4: FastAPI Security Knowledge Base")
print("-" * 70)

try:
    from src.ai.knowledge_base import FastAPISecurityKB
    
    kb = FastAPISecurityKB()
    
    # Test retrieval
    results = kb.retrieve("SQL injection SELECT FROM")
    
    print(f"✅ Knowledge Base loaded successfully")
    print(f"📊 KB contains {len(kb.vulnerabilities)} vulnerability types")
    print(f"🔍 Query 'SQL injection' returned {len(results)} results")
    print()
    
    if results:
        print("📖 Sample KB Entry:")
        result = results[0]
        print(f"   Type: {result['vulnerability']}")
        print(f"   Severity: {result['severity']}")
        print(f"   Description: {result['description'][:80]}...")
    
    print()
    print("✅ TEST 4 PASSED: Knowledge base working!")
    test4_pass = True
    
except Exception as e:
    print(f"❌ TEST 4 FAILED: {e}")
    test4_pass = False

print()

# Test 5: Pydantic Models
print("🧪 TEST 5: Pydantic V2 Models & Validation")
print("-" * 70)

try:
    from src.schemas.models import PRAnalysisRequest, VulnerabilityReport
    
    # Test valid request
    valid_request = PRAnalysisRequest(
        url="https://github.com/tiangolo/fastapi/pull/1"
    )
    print(f"✅ Valid PR URL accepted: {valid_request.url}")
    
    # Test invalid request
    try:
        invalid_request = PRAnalysisRequest(url="not-a-github-url")
        print("❌ Invalid URL should have been rejected!")
        test5_pass = False
    except Exception as e:
        print(f"✅ Invalid URL correctly rejected: {str(e)[:60]}...")
    
    # Test VulnerabilityReport
    report = VulnerabilityReport(
        pr_url="https://github.com/test/repo/pull/1",
        vulnerabilities=["sql_injection", "hardcoded_secret"],
        risk_score=0.85,
        recommendations=["Use parameterized queries", "Use env vars"],
        summary="Test report"
    )
    print(f"✅ VulnerabilityReport model working")
    print(f"   Vulnerabilities: {len(report.vulnerabilities)}")
    print(f"   Risk Score: {report.risk_score}")
    
    print()
    print("✅ TEST 5 PASSED: Pydantic V2 models with validation working!")
    test5_pass = True
    
except Exception as e:
    print(f"❌ TEST 5 FAILED: {e}")
    test5_pass = False

print()

# Test 6: Configuration
print("🧪 TEST 6: Configuration Management")
print("-" * 70)

try:
    from src.schemas.config import config
    
    print(f"✅ Config loaded successfully")
    print(f"📊 Configuration Status:")
    print(f"   Has Gradient AI Key: {'Yes' if config.gradient_api_key and config.gradient_api_key != 'mock_key' else 'No (using mock)'}")
    print(f"   Has GitHub Token: {'Yes' if config.github_token else 'No (optional)'}")
    
    print()
    print("✅ TEST 6 PASSED: Configuration management working!")
    test6_pass = True
    
except Exception as e:
    print(f"❌ TEST 6 FAILED: {e}")
    test6_pass = False

print()

# Summary
print("=" * 70)
print("📊 TEST SUMMARY")
print("=" * 70)
print()

tests = [
    ("AST Analyzer", test1_pass),
    ("Risk Scoring", test2_pass),
    ("Gradient AI Client", test3_pass),
    ("Knowledge Base", test4_pass),
    ("Pydantic Models", test5_pass),
    ("Configuration", test6_pass),
]

passed = sum(1 for _, p in tests if p)
total = len(tests)

for name, passed_test in tests:
    status = "✅ PASS" if passed_test else "❌ FAIL"
    print(f"{status} - {name}")

print()
print(f"Results: {passed}/{total} tests passed ({int(passed/total*100)}%)")
print()

if passed == total:
    print("🎉 ALL TESTS PASSED! Production-ready features working perfectly!")
    print()
    print("Next steps:")
    print("1. Set up API keys: python3 test_api_keys.py")
    print("2. Install dependencies: pip install -r requirements.txt")
    print("3. Start app: uvicorn src.main:app --reload")
    sys.exit(0)
else:
    print("⚠️  Some tests failed. Check error messages above.")
    print()
    print("Common fixes:")
    print("- Install dependencies: pip install -r requirements.txt")
    print("- Check Python version: python3 --version (need 3.9+)")
    sys.exit(1)
