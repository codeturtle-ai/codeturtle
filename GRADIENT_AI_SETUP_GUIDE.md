# DigitalOcean Gradient AI Platform Setup Guide

**Purpose**: Complete guide to get API keys and integrate DigitalOcean Gradient AI Platform  
**Time Required**: 10-15 minutes  
**Difficulty**: Easy  

---

## 🎯 Step 1: Get DigitalOcean API Token

### Option A: DigitalOcean Account (Recommended)

1. **Create/Login to DigitalOcean Account**
   - Go to: https://cloud.digitalocean.com/
   - Sign up or log in with existing account
   - You may need to add payment method (some features have free tier)

2. **Navigate to API Settings**
   - Click on **API** in the left sidebar
   - Or go directly to: https://cloud.digitalocean.com/account/api/tokens

3. **Generate New Token**
   - Click **"Generate New Token"** button
   - **Name**: `fastapi-security-agent-dev` (or your choice)
   - **Scopes**: Select **"Write"** (allows read + write access)
   - **Expiration**: Choose expiration period (or never)
   - Click **"Generate Token"**

4. **IMPORTANT: Copy Token Immediately**
   ```
   Token will look like: dop_v1_abc123xyz456...
   
   ⚠️ WARNING: You can only see this token ONCE!
   Copy it immediately and save it securely.
   ```

5. **Save Your Token**
   - Copy the token
   - We'll add it to `.env` file in Step 3

---

## 🔑 Step 2: Get GitHub Personal Access Token (Optional but Recommended)

**Why?** GitHub API has rate limits. With a token, you get higher limits (5000 requests/hour vs 60).

1. **Go to GitHub Settings**
   - Visit: https://github.com/settings/tokens
   - Or: GitHub → Settings → Developer settings → Personal access tokens → Tokens (classic)

2. **Generate New Token (Classic)**
   - Click **"Generate new token"** → **"Generate new token (classic)"**
   - **Note**: `fastapi-security-agent-github-access`

3. **Set Permissions**
   - Select these scopes:
     - ✅ `repo` (Full control of private repositories)
     - ✅ `public_repo` (Access public repositories)
   - Leave other scopes unchecked

4. **Generate and Copy**
   - Click **"Generate token"** at bottom
   - Copy the token (starts with `ghp_...`)
   - Save it securely

---

## 📝 Step 3: Configure Environment Variables

### Create `.env` File

```bash
cd /Users/apple/HacktoberFest2025

# Create .env file
cat > .env << 'EOF'
# DigitalOcean Gradient AI Platform API Key
GRADIENT_AI_API_KEY=your_digitalocean_token_here

# GitHub Personal Access Token (optional but recommended)
GITHUB_TOKEN=your_github_token_here

# Application Settings
APP_ENV=development
LOG_LEVEL=INFO
EOF
```

### Edit with Your Tokens

Open `.env` in your editor and replace:
```bash
# Replace this:
GRADIENT_AI_API_KEY=your_digitalocean_token_here

# With your actual token:
GRADIENT_AI_API_KEY=dop_v1_abc123xyz456...


# Replace this:
GITHUB_TOKEN=your_github_token_here

# With your actual token:
GITHUB_TOKEN=ghp_xyz123abc456...
```

### Verify `.env` File

```bash
# Check file exists
ls -la .env

# View file (be careful - contains secrets!)
cat .env

# Should show:
# GRADIENT_AI_API_KEY=dop_v1_...
# GITHUB_TOKEN=ghp_...
```

---

## 🔐 Step 4: Secure Your Environment File

### Add to `.gitignore` (Already Done)

Your `.gitignore` already includes `.env`, but let's verify:

```bash
# Check if .env is in .gitignore
grep -n "\.env" .gitignore

# Should see:
# .env
# .env.local
# .env.*.local
```

### Verify Not Tracked by Git

```bash
# This should NOT show .env file
git status

# Double check
git ls-files | grep .env
# Should return nothing (empty)
```

**⚠️ CRITICAL: Never commit `.env` to git!**

---

## 🧪 Step 5: Test Your API Keys

### Test DigitalOcean API

```bash
# Test with curl
curl -X GET \
  -H "Authorization: Bearer YOUR_DIGITALOCEAN_TOKEN" \
  https://api.digitalocean.com/v2/account

# Should return JSON with account info
# If you get 401 Unauthorized → token is invalid
# If you get 200 OK → token works!
```

### Test GitHub API

```bash
# Test without token (low rate limit)
curl https://api.github.com/rate_limit

# Test with token (high rate limit)
curl -H "Authorization: Bearer YOUR_GITHUB_TOKEN" \
  https://api.github.com/rate_limit

# Should show:
# "limit": 5000 (with token) vs 60 (without)
```

### Test in Python

Create a test script:

```bash
cat > test_api_keys.py << 'EOF'
#!/usr/bin/env python3
"""Test API keys configuration."""

import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def test_gradient_ai_key():
    """Test DigitalOcean Gradient AI key."""
    api_key = os.getenv("GRADIENT_AI_API_KEY")
    
    if not api_key:
        print("❌ GRADIENT_AI_API_KEY not found in .env")
        return False
    
    if api_key == "your_digitalocean_token_here":
        print("⚠️  GRADIENT_AI_API_KEY still has placeholder value")
        return False
    
    if not api_key.startswith("dop_"):
        print(f"⚠️  GRADIENT_AI_API_KEY format unexpected (got: {api_key[:10]}...)")
        print("   Expected format: dop_v1_...")
        return False
    
    print(f"✅ GRADIENT_AI_API_KEY configured: {api_key[:15]}...{api_key[-4:]}")
    return True

def test_github_token():
    """Test GitHub token."""
    token = os.getenv("GITHUB_TOKEN")
    
    if not token:
        print("⚠️  GITHUB_TOKEN not found (optional but recommended)")
        return True  # Optional, so not a failure
    
    if token == "your_github_token_here":
        print("⚠️  GITHUB_TOKEN still has placeholder value")
        return True  # Optional
    
    if not token.startswith("ghp_"):
        print(f"⚠️  GITHUB_TOKEN format unexpected (got: {token[:10]}...)")
        print("   Expected format: ghp_...")
        return True  # Optional
    
    print(f"✅ GITHUB_TOKEN configured: {token[:10]}...{token[-4:]}")
    return True

def main():
    print("=" * 60)
    print("Testing API Keys Configuration")
    print("=" * 60)
    print()
    
    gradient_ok = test_gradient_ai_key()
    github_ok = test_github_token()
    
    print()
    print("=" * 60)
    
    if gradient_ok and github_ok:
        print("✅ All API keys configured correctly!")
        print()
        print("Next steps:")
        print("1. Install dependencies: pip install -r requirements.txt")
        print("2. Start the app: uvicorn src.main:app --reload")
        print("3. Test analysis: curl -X POST http://localhost:8000/analyze \\")
        print("     -H 'Content-Type: application/json' \\")
        print("     -d '{\"url\": \"https://github.com/tiangolo/fastapi/pull/1\"}'")
        return 0
    else:
        print("❌ API key configuration issues detected")
        print()
        print("Please:")
        print("1. Check your .env file exists")
        print("2. Verify tokens are correctly copied")
        print("3. Ensure no extra spaces or quotes")
        return 1

if __name__ == "__main__":
    exit(main())
EOF

chmod +x test_api_keys.py
```

### Run the Test

```bash
python3 test_api_keys.py
```

**Expected Output**:
```
============================================================
Testing API Keys Configuration
============================================================

✅ GRADIENT_AI_API_KEY configured: dop_v1_abc123...xyz4
✅ GITHUB_TOKEN configured: ghp_xyz12...abc4

============================================================
✅ All API keys configured correctly!

Next steps:
1. Install dependencies: pip install -r requirements.txt
2. Start the app: uvicorn src.main:app --reload
3. Test analysis: curl -X POST http://localhost:8000/analyze ...
```

---

## 🚀 Step 6: Install Dependencies and Start App

### Install Python Dependencies

```bash
# Install all required packages
pip install -r requirements.txt

# Or with pip3
pip3 install -r requirements.txt

# Should install:
# - fastapi
# - uvicorn
# - pydantic
# - python-dotenv (for .env loading)
# - httpx (for API calls)
# - tenacity (for retries)
# - slowapi (for rate limiting)
# - jinja2 (for templates)
# - pytest (for testing)
```

### Verify Installation

```bash
# Check key packages
python3 -c "import fastapi; print(f'FastAPI: {fastapi.__version__}')"
python3 -c "import httpx; print(f'httpx: {httpx.__version__}')"
python3 -c "import dotenv; print('python-dotenv: OK')"
```

### Start the Application

```bash
# Start with auto-reload (development)
uvicorn src.main:app --reload --host 0.0.0.0 --port 8000

# Or with more verbose logging
uvicorn src.main:app --reload --host 0.0.0.0 --port 8000 --log-level debug
```

**Expected Output**:
```
INFO:     Will watch for changes in these directories: ['/Users/apple/HacktoberFest2025']
INFO:     Uvicorn running on http://0.0.0.0:8000 (Press CTRL+C to quit)
INFO:     Started reloader process [12345] using StatReload
INFO:     Started server process [12346]
INFO:     Waiting for application startup.
INFO:     Application startup complete.
```

---

## 🧪 Step 7: Test Gradient AI Integration

### Test 1: Health Check

```bash
# Should return 200 OK
curl http://localhost:8000/health

# Expected:
# {"status":"healthy","timestamp":"2025-10-05T...","version":"1.0.0"}
```

### Test 2: Analyze with Mock Data (No API Key)

```bash
# Test without API key (uses fallback analysis)
curl -X POST http://localhost:8000/analyze \
  -H "Content-Type: application/json" \
  -d '{"url": "https://github.com/tiangolo/fastapi/pull/1"}' | jq
```

**Expected Response**:
```json
{
  "pr_url": "https://github.com/tiangolo/fastapi/pull/1",
  "vulnerabilities": [
    "sql_injection",
    "hardcoded_secret"
  ],
  "risk_score": 0.65,
  "recommendations": [
    "Use parameterized queries",
    "Move secrets to environment variables"
  ],
  "summary": "Found 2 vulnerabilities with medium risk level..."
}
```

### Test 3: Analyze with Real Gradient AI

```bash
# With your API key configured, this will use real AI
curl -X POST http://localhost:8000/analyze \
  -H "Content-Type: application/json" \
  -d '{"url": "https://github.com/tiangolo/fastapi/pull/1"}' | jq

# Should take 2-5 seconds (AI processing)
# Response will include AI analysis results
```

### Test 4: AST Analysis Only

Create a simple test:

```bash
cat > test_ast_only.py << 'EOF'
from src.detection.ast_analyzer import ASTAnalyzer

code = """
password = "hardcoded_secret_123"
api_key = "sk_live_abc123xyz456"
eval("print('danger')")
cursor.execute("SELECT * FROM users WHERE id = " + user_id)
"""

analyzer = ASTAnalyzer()
findings = analyzer.analyze_code(code)

print(f"\n{'='*60}")
print(f"AST Analysis Results: {len(findings)} vulnerabilities found")
print(f"{'='*60}\n")

for i, finding in enumerate(findings, 1):
    print(f"{i}. {finding['vulnerability'].upper()}")
    print(f"   Line: {finding.get('line', 'N/A')}")
    print(f"   Severity: {finding['severity']}")
    print(f"   Confidence: {finding['confidence']}")
    print(f"   Description: {finding['description']}")
    if 'remediation' in finding:
        print(f"   Fix: {finding['remediation']}")
    print()
EOF

python3 test_ast_only.py
```

**Expected Output**:
```
============================================================
AST Analysis Results: 4 vulnerabilities found
============================================================

1. HARDCODED_PASSWORD
   Line: 2
   Severity: critical
   Confidence: 0.95
   Description: Hardcoded hardcoded password detected

2. HARDCODED_API_KEY
   Line: 3
   Severity: critical
   Confidence: 0.95
   Description: Hardcoded hardcoded api key detected

3. CODE_EXECUTION
   Line: 4
   Severity: critical
   Confidence: 0.95
   Description: Use of eval() enables arbitrary code execution
   Fix: Remove eval/exec calls and use safer alternatives

4. SQL_INJECTION
   Line: 5
   Severity: critical
   Confidence: 0.9
   Description: SQL injection via string concatenation
   Fix: Use parameterized queries instead
```

---

## 🔧 Troubleshooting

### Issue: "ModuleNotFoundError: No module named 'dotenv'"

**Fix**:
```bash
pip install python-dotenv
```

### Issue: "ModuleNotFoundError: No module named 'slowapi'"

**Fix**:
```bash
pip install slowapi
```

### Issue: ".env file not loaded"

**Fix**:
```bash
# Verify .env exists
ls -la .env

# Check file has correct format (no spaces around =)
cat .env

# Correct format:
GRADIENT_AI_API_KEY=dop_v1_abc123

# Wrong format (spaces):
GRADIENT_AI_API_KEY = dop_v1_abc123
```

### Issue: "401 Unauthorized" from DigitalOcean

**Possible causes**:
1. Token expired
2. Token copied incorrectly (extra spaces, newlines)
3. Token doesn't have correct scopes

**Fix**:
```bash
# Test token directly
curl -X GET \
  -H "Authorization: Bearer YOUR_TOKEN" \
  https://api.digitalocean.com/v2/account

# If 401, regenerate token on DigitalOcean
```

### Issue: "404 Not Found" from Gradient AI endpoint

**Note**: DigitalOcean Gradient AI may have a different endpoint structure. The code has fallback mechanisms:
1. First tries real API
2. If that fails, uses enhanced pattern-based analysis
3. You still get results, just without AI insights

**To fix for real AI**:
Check DigitalOcean docs for actual Gradient AI endpoint and update `src/clients/gradient_ai.py`:
```python
BASE_URL = "https://api.digitalocean.com/v2/ai"  # Update if different
```

---

## 📊 API Usage Limits

### DigitalOcean API
- **Rate Limit**: 5000 requests/hour (with token)
- **Cost**: Check DigitalOcean pricing for Gradient AI Platform
- **Free Tier**: May have limited free credits

### GitHub API
- **Without Token**: 60 requests/hour per IP
- **With Token**: 5000 requests/hour
- **Cost**: Free for public repos

---

## ✅ Quick Reference Card

```bash
# 1. Get API keys
# DigitalOcean: https://cloud.digitalocean.com/account/api/tokens
# GitHub: https://github.com/settings/tokens

# 2. Create .env file
cat > .env << 'EOF'
GRADIENT_AI_API_KEY=dop_v1_your_token_here
GITHUB_TOKEN=ghp_your_token_here
APP_ENV=development
LOG_LEVEL=INFO
EOF

# 3. Test keys
python3 test_api_keys.py

# 4. Install deps
pip install -r requirements.txt

# 5. Start app
uvicorn src.main:app --reload

# 6. Test
curl http://localhost:8000/health
```

---

## 🎯 Next Steps After Setup

Once your API keys are configured and working:

1. ✅ **Test the AST analyzer** (works without API keys)
2. ✅ **Test the risk scoring** (works without API keys)
3. ✅ **Test with real PR** (needs GitHub token for best results)
4. ✅ **Monitor API usage** (check DigitalOcean dashboard)
5. ✅ **Review logs** for any errors

---

## 📚 Additional Resources

- **DigitalOcean Gradient AI Docs**: https://docs.digitalocean.com/products/gradient-ai-platform/
- **GitHub API Docs**: https://docs.github.com/en/rest
- **FastAPI Docs**: https://fastapi.tiangolo.com/
- **Project README**: README.md

---

**Questions?** Check the logs:
```bash
# Application logs
tail -f logs/app.log

# Or check uvicorn output in terminal
```

**Success Criteria**: ✅
- `.env` file created with tokens
- `test_api_keys.py` shows all green checkmarks
- App starts without errors
- `/health` endpoint returns 200 OK
- AST analysis detects vulnerabilities

You're ready to analyze code for security vulnerabilities! 🚀

