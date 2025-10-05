# 🚀 Quick Start Integration Guide
## Get FastAPI Security Agent Running in 5 Minutes

**For**: Developers who want to get started quickly  
**Time**: 5-10 minutes  
**Difficulty**: Beginner  

---

## ⚡ **Super Quick Setup (TL;DR)**

```bash
# 1. Run the setup script
./setup.sh

# 2. Edit environment variables
nano .env  # Add your API keys

# 3. Start the server
source venv/bin/activate
uvicorn src.main:app --reload

# 4. Test it works
curl http://localhost:8000/health
```

**Done!** 🎉 Your security agent is running at http://localhost:8000

---

## 📋 **Step-by-Step Guide**

### **Step 1: Prerequisites Check**
```bash
# Check Python version (need 3.9+)
python3 --version

# If Python is missing, install it:
# macOS: brew install python@3.11
# Ubuntu: sudo apt install python3.11
```

### **Step 2: Automated Setup**
```bash
# Make setup script executable and run it
chmod +x setup.sh
./setup.sh

# This will:
# ✅ Create virtual environment
# ✅ Install all dependencies  
# ✅ Create .env file
# ✅ Test basic functionality
```

### **Step 3: Configure API Keys**
```bash
# Edit the environment file
nano .env

# Add your API keys:
GRADIENT_AI_API_KEY=your_digitalocean_ai_key_here
GITHUB_TOKEN=your_github_token_here
```

**Getting API Keys:**
- **DigitalOcean AI**: https://cloud.digitalocean.com/account/api/tokens
- **GitHub Token**: https://github.com/settings/tokens

### **Step 4: Start the Server**
```bash
# Activate virtual environment
source venv/bin/activate

# Start development server
uvicorn src.main:app --reload --host 0.0.0.0 --port 8000
```

### **Step 5: Test Everything Works**
```bash
# In another terminal, test the API
./test_api_endpoints.sh

# Or manually test:
curl http://localhost:8000/health
curl -X POST "http://localhost:8000/analyze" \
     -H "Content-Type: application/json" \
     -d '{"url": "https://github.com/tiangolo/fastapi/pull/1"}'
```

---

## 🌐 **Access Points**

Once running, you can access:

- **🏠 Web Interface**: http://localhost:8000/ui
- **📚 API Docs**: http://localhost:8000/docs  
- **❤️ Health Check**: http://localhost:8000/health
- **📊 Report**: http://localhost:8000/report

---

## 🧪 **Quick Test Commands**

### **Test Vulnerability Detection:**
```bash
# Test with a real GitHub PR
curl -X POST "http://localhost:8000/analyze" \
     -H "Content-Type: application/json" \
     -d '{"url": "https://github.com/tiangolo/fastapi/pull/1"}'
```

### **Test Batch Analysis:**
```bash
# Analyze multiple PRs
curl -X POST "http://localhost:8000/scan" \
     -H "Content-Type: application/json" \
     -d '[
         "https://github.com/tiangolo/fastapi/pull/1",
         "https://github.com/tiangolo/fastapi/pull/2"
     ]'
```

### **Test Web Interface:**
```bash
# Open in browser
open http://localhost:8000/ui

# Or test with curl
curl http://localhost:8000/ui
```

---

## 🔧 **Configuration Options**

### **Development Mode (Default):**
```bash
# In .env file:
APP_ENV=development
DEBUG=true
MOCK_MODE=true  # Uses fallbacks when APIs fail
```

### **Production Mode:**
```bash
# In .env file:
APP_ENV=production
DEBUG=false
MOCK_MODE=false  # Requires real API responses
```

### **Testing Mode:**
```bash
# In .env file:
TEST_MODE=true
LOG_LEVEL=DEBUG
```

---

## 🚨 **Troubleshooting**

### **Common Issues:**

#### **"ModuleNotFoundError"**
```bash
# Solution: Reinstall dependencies
pip install -r requirements.txt --force-reinstall
```

#### **"Server not starting"**
```bash
# Check if port is in use
lsof -i :8000

# Use different port
uvicorn src.main:app --reload --port 8001
```

#### **"API key errors"**
```bash
# Check environment variables
env | grep -E "(GRADIENT|GITHUB)"

# Test without API keys (uses fallbacks)
export MOCK_MODE=true
```

#### **"GitHub rate limiting"**
```bash
# Check rate limit status
curl -H "Authorization: token YOUR_TOKEN" \
     https://api.github.com/rate_limit
```

### **Debug Mode:**
```bash
# Enable detailed logging
export LOG_LEVEL=DEBUG
export DEBUG=true
uvicorn src.main:app --reload --log-level debug
```

---

## 📊 **Verification Checklist**

After setup, verify these work:

- [ ] **Health check**: `curl http://localhost:8000/health`
- [ ] **Web interface**: Open http://localhost:8000/ui
- [ ] **API docs**: Open http://localhost:8000/docs
- [ ] **Basic analysis**: Test with a GitHub PR URL
- [ ] **Error handling**: Test with invalid URL
- [ ] **Fallback mode**: Works without API keys

---

## 🎯 **What You Get**

### **✅ Working Features:**
- **Real vulnerability detection** (AST + pattern analysis)
- **GitHub PR analysis** (with or without token)
- **AI-powered analysis** (with DigitalOcean API key)
- **Multi-agent system** (6 specialized agents)
- **Web interface** for easy testing
- **REST API** for integration
- **Comprehensive error handling**

### **🔧 **Fallback Capabilities:**
- **Works without API keys** (uses enhanced pattern matching)
- **Graceful degradation** when APIs fail
- **Mock data** for testing and demos
- **Offline analysis** for basic vulnerability detection

---

## 🚀 **Next Steps**

### **For Development:**
1. **Explore the code**: Check out `src/` directory
2. **Add features**: Extend the agents or add new vulnerability types
3. **Customize**: Modify the web interface or API endpoints
4. **Test**: Add more test cases in `test_implementation.py`

### **For Production:**
1. **Get API keys**: Set up DigitalOcean and GitHub integrations
2. **Configure security**: Set strong secret keys and CORS origins
3. **Deploy**: Use Docker or DigitalOcean App Platform
4. **Monitor**: Set up logging and health checks

### **For Hackathon:**
1. **Prepare demo**: Test with interesting GitHub PRs
2. **Collect metrics**: Run analysis on multiple repositories
3. **Create presentation**: Show real vulnerability detection
4. **Document results**: Highlight the AI integration and impact

---

## 📞 **Need Help?**

### **Quick Commands:**
```bash
# Health check
python3 test_implementation.py

# Full API test
./test_api_endpoints.sh

# Check logs
tail -f logs/security_agent.log

# Restart server
pkill -f uvicorn && uvicorn src.main:app --reload
```

### **Documentation:**
- **Full setup guide**: `SETUP_AND_INTEGRATION_GUIDE.md`
- **Implementation details**: `IMPLEMENTATION_COMPLETE_REPORT.md`
- **Architecture**: `TECHNICAL_ARCHITECTURE.md`

---

## 🎉 **You're Ready!**

Your FastAPI Security Agent is now running with:
- ✅ **Real vulnerability detection**
- ✅ **AI integration capabilities** 
- ✅ **GitHub API integration**
- ✅ **Production-ready architecture**
- ✅ **Comprehensive testing**

**Start analyzing some GitHub PRs and see the magic happen!** 🔍✨