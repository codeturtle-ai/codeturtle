# 🚀 Complete Setup & Integration Guide
## FastAPI Security Agent - Environment Setup & Testing

**Last Updated**: October 2025  
**For**: Development Team & Hackathon Participants  
**Difficulty**: Beginner to Intermediate  

---

## 📋 **Quick Start Checklist**

- [ ] Python 3.9+ installed
- [ ] Dependencies installed
- [ ] Environment variables configured
- [ ] Basic functionality tested
- [ ] API integrations configured
- [ ] Full system tested

---

## 🔧 **1. System Requirements**

### **Minimum Requirements:**
- **Python**: 3.9 or higher
- **RAM**: 2GB minimum, 4GB recommended
- **Storage**: 1GB free space
- **Network**: Internet connection for API calls

### **Check Your Python Version:**
```bash
python3 --version
# Should show: Python 3.9.x or higher
```

### **If Python is Missing:**
```bash
# macOS (using Homebrew)
brew install python@3.11

# Ubuntu/Debian
sudo apt update
sudo apt install python3.11 python3.11-pip

# Windows
# Download from https://python.org/downloads/
```

---

## 📦 **2. Installation & Dependencies**

### **Step 1: Clone and Navigate**
```bash
cd /Users/apple/HacktoberFest2025
# or wherever your project is located
```

### **Step 2: Create Virtual Environment (Recommended)**
```bash
# Create virtual environment
python3 -m venv venv

# Activate it
# On macOS/Linux:
source venv/bin/activate

# On Windows:
# venv\Scripts\activate

# You should see (venv) in your terminal prompt
```

### **Step 3: Install Dependencies**
```bash
# Install all required packages
pip install -r requirements.txt

# If you get errors, try upgrading pip first:
pip install --upgrade pip
pip install -r requirements.txt
```

### **Step 4: Verify Installation**
```bash
# Test basic imports
python3 -c "import fastapi, uvicorn, pydantic, httpx; print('✅ Core dependencies installed')"

# Test our modules
python3 test_implementation.py
```

---

## 🔐 **3. Environment Variables Setup**

### **Step 1: Create Environment File**
```bash
# Copy the example file
cp .env.example .env

# Or create manually
touch .env
```

### **Step 2: Configure .env File**
Open `.env` in your text editor and add:

```bash
# =============================================================================
# FastAPI Security Agent - Environment Configuration
# =============================================================================

# DigitalOcean Gradient AI Platform
# Get your API key from: https://cloud.digitalocean.com/account/api/tokens
GRADIENT_AI_API_KEY=your_digitalocean_ai_key_here

# GitHub API Integration
# Get your token from: https://github.com/settings/tokens
# Required scopes: repo (for private repos) or public_repo (for public only)
GITHUB_TOKEN=your_github_token_here

# Application Configuration
APP_ENV=development
LOG_LEVEL=INFO
DEBUG=true

# API Rate Limiting
RATE_LIMIT_PER_MINUTE=10
RATE_LIMIT_BURST=5

# Security Settings
SECRET_KEY=your-secret-key-for-sessions
ALLOWED_HOSTS=localhost,127.0.0.1

# Database (Optional - for production)
DATABASE_URL=sqlite:///./security_agent.db

# Redis (Optional - for caching)
REDIS_URL=redis://localhost:6379/0

# =============================================================================
# Testing Configuration
# =============================================================================

# Test GitHub Repository (for testing)
TEST_GITHUB_REPO=tiangolo/fastapi
TEST_PR_URL=https://github.com/tiangolo/fastapi/pull/1

# Mock Mode (set to true to use fallback analysis without API keys)
MOCK_MODE=false
```

### **Step 3: Secure Your .env File**
```bash
# Make sure .env is in .gitignore
echo ".env" >> .gitignore

# Set proper permissions (Unix/macOS)
chmod 600 .env
```

---

## 🔑 **4. API Keys & Integrations Setup**

### **4.1 DigitalOcean Gradient AI Platform**

#### **Get Your API Key:**
1. Go to [DigitalOcean Cloud Console](https://cloud.digitalocean.com/)
2. Sign up/Login to your account
3. Navigate to **API** → **Tokens & Keys**
4. Click **Generate New Token**
5. Name: `FastAPI-Security-Agent`
6. Scopes: Select **Read** and **Write**
7. Copy the generated token

#### **Configure in .env:**
```bash
GRADIENT_AI_API_KEY=dop_v1_1234567890abcdef1234567890abcdef
```

#### **Test DigitalOcean Integration:**
```bash
# Test with API key
python3 -c "
import sys
sys.path.append('src')
from clients.gradient_ai import GradientAIClient
import asyncio
import os

async def test():
    client = GradientAIClient(os.getenv('GRADIENT_AI_API_KEY'))
    result = await client.analyze_code('password = \"test123\"')
    print('✅ DigitalOcean AI:', result.get('analysis_method', 'AI_ANALYSIS'))

asyncio.run(test())
"
```

### **4.2 GitHub API Integration**

#### **Get Your GitHub Token:**
1. Go to [GitHub Settings → Developer settings → Personal access tokens](https://github.com/settings/tokens)
2. Click **Generate new token (classic)**
3. Name: `FastAPI-Security-Agent`
4. Expiration: Choose appropriate duration
5. Scopes needed:
   - `public_repo` (for public repositories)
   - `repo` (for private repositories - if needed)
6. Click **Generate token**
7. Copy the token immediately (you won't see it again)

#### **Configure in .env:**
```bash
GITHUB_TOKEN=ghp_1234567890abcdef1234567890abcdef12345678
```

#### **Test GitHub Integration:**
```bash
# Test with token
python3 -c "
import sys
sys.path.append('src')
from clients.github_client import GitHubClient
import asyncio
import os

async def test():
    client = GitHubClient(os.getenv('GITHUB_TOKEN'))
    try:
        parsed = client._parse_pr_url('https://github.com/tiangolo/fastapi/pull/1')
        print('✅ GitHub URL parsing:', parsed)
        
        # Test API call (if token is valid)
        if os.getenv('GITHUB_TOKEN'):
            metadata = await client.get_pr_metadata('https://github.com/tiangolo/fastapi/pull/1')
            print('✅ GitHub API:', metadata.get('title', 'Success'))
    except Exception as e:
        print('⚠️ GitHub API (using fallback):', str(e))

asyncio.run(test())
"
```

---

## 🧪 **5. Testing Guide**

### **5.1 Basic Functionality Test**
```bash
# Run our comprehensive test suite
python3 test_implementation.py

# Expected output:
# ✅ Enhanced Fallback Analysis: X vulnerabilities detected
# ✅ AST Analyzer: X vulnerabilities detected
# ✅ Knowledge Base: X matches found
# ✅ Multi-Agent Router: Working
```

### **5.2 FastAPI Application Test**
```bash
# Start the FastAPI server
uvicorn src.main:app --reload --host 0.0.0.0 --port 8000

# In another terminal, test endpoints:
curl http://localhost:8000/health

# Expected response:
# {"status":"healthy","timestamp":"...","version":"1.0.0"}
```

### **5.3 Web Interface Test**
```bash
# With server running, open browser:
open http://localhost:8000/ui

# Or test with curl:
curl http://localhost:8000/
```

### **5.4 API Endpoint Tests**
```bash
# Test analyze endpoint
curl -X POST "http://localhost:8000/analyze" \
     -H "Content-Type: application/json" \
     -d '{"url": "https://github.com/tiangolo/fastapi/pull/1"}'

# Test batch scan
curl -X POST "http://localhost:8000/scan" \
     -H "Content-Type: application/json" \
     -d '["https://github.com/tiangolo/fastapi/pull/1"]'

# Test report endpoint
curl "http://localhost:8000/report"
```

### **5.5 Integration Tests**
```bash
# Test with real PR (requires GitHub token)
python3 -c "
import sys
sys.path.append('src')
from ai.agent import SecurityAgent
from clients.gradient_ai import GradientAIClient
import asyncio
import os

async def test_full_integration():
    ai_client = GradientAIClient(os.getenv('GRADIENT_AI_API_KEY'))
    agent = SecurityAgent(ai_client, os.getenv('GITHUB_TOKEN'))
    
    # Test with a real PR
    pr_url = 'https://github.com/tiangolo/fastapi/pull/1'
    report = await agent.analyze_pull_request(pr_url)
    
    print(f'✅ Full Integration Test:')
    print(f'   PR: {report.pr_url}')
    print(f'   Vulnerabilities: {len(report.vulnerabilities)}')
    print(f'   Risk Score: {report.risk_score}')
    print(f'   Summary: {report.summary[:100]}...')

asyncio.run(test_full_integration())
"
```

---

## 🔧 **6. Configuration Options**

### **6.1 Development vs Production**

#### **Development Configuration:**
```bash
# .env for development
APP_ENV=development
DEBUG=true
LOG_LEVEL=DEBUG
MOCK_MODE=true  # Use fallbacks when APIs fail
RATE_LIMIT_PER_MINUTE=100  # Higher limits for testing
```

#### **Production Configuration:**
```bash
# .env for production
APP_ENV=production
DEBUG=false
LOG_LEVEL=INFO
MOCK_MODE=false  # Require real API responses
RATE_LIMIT_PER_MINUTE=10  # Stricter limits
SECRET_KEY=your-strong-secret-key-here
ALLOWED_HOSTS=yourdomain.com,api.yourdomain.com
```

### **6.2 Performance Tuning**
```bash
# High-performance configuration
CONCURRENT_ANALYSES=10  # Max concurrent PR analyses
ANALYSIS_TIMEOUT=300    # 5 minutes timeout
CACHE_TTL=3600         # 1 hour cache
MAX_FILE_SIZE=1048576  # 1MB max file size
MAX_PR_FILES=50        # Max files per PR
```

### **6.3 Security Settings**
```bash
# Security configuration
ENABLE_RATE_LIMITING=true
REQUIRE_API_KEY=false  # Set to true for production
CORS_ORIGINS=http://localhost:3000,https://yourdomain.com
SECURE_COOKIES=true    # For HTTPS
```

---

## 🚨 **7. Troubleshooting Guide**

### **7.1 Common Issues & Solutions**

#### **Issue: "ModuleNotFoundError: No module named 'tenacity'"**
```bash
# Solution: Install missing dependencies
pip install tenacity slowapi jinja2 aiofiles

# Or reinstall all requirements
pip install -r requirements.txt --force-reinstall
```

#### **Issue: "TypeError: unsupported operand type(s) for |"**
```bash
# Solution: Python version too old
python3 --version  # Should be 3.9+

# Upgrade Python or use older syntax
# We've already fixed this in the code
```

#### **Issue: GitHub API rate limiting**
```bash
# Solution: Add GitHub token or wait
# Check rate limit status:
curl -H "Authorization: token YOUR_TOKEN" https://api.github.com/rate_limit
```

#### **Issue: DigitalOcean AI API errors**
```bash
# Solution: Check API key and endpoint
# Test with curl:
curl -H "Authorization: Bearer YOUR_API_KEY" \
     -H "Content-Type: application/json" \
     https://api.digitalocean.com/v2/ai/models
```

### **7.2 Debug Mode**
```bash
# Enable debug logging
export LOG_LEVEL=DEBUG
export DEBUG=true

# Run with verbose output
uvicorn src.main:app --reload --log-level debug
```

### **7.3 Health Checks**
```bash
# Check all components
python3 -c "
import sys
sys.path.append('src')

# Test imports
try:
    from clients.gradient_ai import GradientAIClient
    print('✅ Gradient AI client')
except Exception as e:
    print(f'❌ Gradient AI client: {e}')

try:
    from clients.github_client import GitHubClient
    print('✅ GitHub client')
except Exception as e:
    print(f'❌ GitHub client: {e}')

try:
    from ai.agent import SecurityAgent
    print('✅ Security agent')
except Exception as e:
    print(f'❌ Security agent: {e}')

try:
    from detection.ast_analyzer import ASTAnalyzer
    print('✅ AST analyzer')
except Exception as e:
    print(f'❌ AST analyzer: {e}')
"
```

---

## 🎯 **8. Testing Scenarios**

### **8.1 Test Cases for Demo**

#### **Test Case 1: Basic Vulnerability Detection**
```python
# Test code with known vulnerabilities
test_code = '''
# Hardcoded secret
password = "admin123"
api_key = "sk-1234567890abcdef"

# SQL injection
def get_user(user_id):
    query = "SELECT * FROM users WHERE id = " + user_id
    return execute(query)

# SSTI
def render_template(user_input):
    return eval(user_input)

# Command injection
import subprocess
def run_command(cmd):
    subprocess.run(f"ls {cmd}", shell=True)
'''

# Expected results:
# - 4+ vulnerabilities detected
# - Risk score > 0.7
# - Specific recommendations for each issue
```

#### **Test Case 2: Real GitHub PR Analysis**
```bash
# Test with actual FastAPI repository PRs
TEST_PRS=(
    "https://github.com/tiangolo/fastapi/pull/1"
    "https://github.com/tiangolo/fastapi/pull/100"
    "https://github.com/encode/starlette/pull/1"
)

for pr in "${TEST_PRS[@]}"; do
    echo "Testing: $pr"
    curl -X POST "http://localhost:8000/analyze" \
         -H "Content-Type: application/json" \
         -d "{\"url\": \"$pr\"}"
    echo ""
done
```

#### **Test Case 3: Batch Analysis**
```bash
# Test batch processing
curl -X POST "http://localhost:8000/scan" \
     -H "Content-Type: application/json" \
     -d '[
         "https://github.com/tiangolo/fastapi/pull/1",
         "https://github.com/tiangolo/fastapi/pull/2",
         "https://github.com/tiangolo/fastapi/pull/3"
     ]'
```

### **8.2 Performance Testing**
```bash
# Load testing with Apache Bench (if installed)
ab -n 100 -c 10 http://localhost:8000/health

# Or with curl in a loop
for i in {1..10}; do
    time curl -s http://localhost:8000/health > /dev/null
done
```

---

## 📊 **9. Monitoring & Logging**

### **9.1 Log Configuration**
```bash
# View logs in real-time
tail -f logs/security_agent.log

# Or with uvicorn
uvicorn src.main:app --log-config logging.conf
```

### **9.2 Health Monitoring**
```bash
# Create monitoring script
cat > monitor.sh << 'EOF'
#!/bin/bash
while true; do
    response=$(curl -s -o /dev/null -w "%{http_code}" http://localhost:8000/health)
    if [ $response -eq 200 ]; then
        echo "$(date): ✅ Service healthy"
    else
        echo "$(date): ❌ Service unhealthy (HTTP $response)"
    fi
    sleep 30
done
EOF

chmod +x monitor.sh
./monitor.sh
```

---

## 🚀 **10. Deployment Guide**

### **10.1 Local Development**
```bash
# Development server
uvicorn src.main:app --reload --host 0.0.0.0 --port 8000

# With custom configuration
uvicorn src.main:app --reload --env-file .env.development
```

### **10.2 Production Deployment**
```bash
# Production server (with Gunicorn)
pip install gunicorn
gunicorn src.main:app -w 4 -k uvicorn.workers.UvicornWorker --bind 0.0.0.0:8000

# With Docker
docker build -t fastapi-security-agent .
docker run -p 8000:8000 --env-file .env fastapi-security-agent
```

### **10.3 DigitalOcean App Platform**
```yaml
# app.yaml for DigitalOcean deployment
name: fastapi-security-agent
services:
- name: api
  source_dir: /
  github:
    repo: your-username/HacktoberFest2025
    branch: main
  run_command: uvicorn src.main:app --host 0.0.0.0 --port $PORT
  environment_slug: python
  instance_count: 1
  instance_size_slug: basic-xxs
  envs:
  - key: GRADIENT_AI_API_KEY
    value: ${GRADIENT_AI_API_KEY}
  - key: GITHUB_TOKEN
    value: ${GITHUB_TOKEN}
```

---

## ✅ **11. Final Verification Checklist**

### **Before Demo/Production:**
- [ ] All dependencies installed (`pip list | grep -E "(fastapi|uvicorn|pydantic|httpx)"`)
- [ ] Environment variables configured (`.env` file exists and populated)
- [ ] Basic tests pass (`python3 test_implementation.py`)
- [ ] FastAPI server starts (`uvicorn src.main:app --reload`)
- [ ] Health endpoint responds (`curl http://localhost:8000/health`)
- [ ] Web interface loads (`open http://localhost:8000/ui`)
- [ ] API endpoints work (`curl -X POST http://localhost:8000/analyze`)
- [ ] GitHub integration works (with token)
- [ ] AI integration works (with API key)
- [ ] Error handling graceful (without API keys)

### **For Hackathon Demo:**
- [ ] Demo PR URLs ready
- [ ] Test vulnerabilities prepared
- [ ] Performance metrics collected
- [ ] Error scenarios tested
- [ ] Presentation materials ready

---

## 🆘 **12. Getting Help**

### **If You're Stuck:**

1. **Check the logs**: Look for error messages in terminal output
2. **Verify environment**: Ensure all environment variables are set
3. **Test components**: Run `python3 test_implementation.py`
4. **Check dependencies**: Run `pip list` to verify installations
5. **Review this guide**: Double-check each step

### **Common Commands Reference:**
```bash
# Quick health check
python3 test_implementation.py

# Start development server
uvicorn src.main:app --reload

# Test API endpoint
curl http://localhost:8000/health

# Check environment variables
env | grep -E "(GRADIENT|GITHUB)"

# Reinstall dependencies
pip install -r requirements.txt --force-reinstall
```

---

**🎉 You're now ready to run the FastAPI Security Agent with full functionality!**

This guide covers everything from basic setup to production deployment. Your system should now be capable of real vulnerability detection using AI and GitHub integration.