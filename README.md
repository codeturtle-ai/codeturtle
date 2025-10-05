# FastAPI Security Agent 🚀

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.104.1-green.svg)](https://fastapi.tiangolo.com/)
[![DigitalOcean](https://img.shields.io/badge/DigitalOcean-Gradient%20AI-blue.svg)](https://docs.digitalocean.com/products/gradient-ai-platform/)

An enterprise-grade, AI-powered open-source tool for automated code vulnerability detection in FastAPI projects, leveraging DigitalOcean's Gradient AI Platform. This production-ready security scanner transforms GitHub PRs into secure, actionable insights.

## 🎯 Problem Statement
FastAPI applications are increasingly popular, but developers often lack automated security analysis tools. Manual code reviews miss critical vulnerabilities like SQL injection, hardcoded secrets, and authentication gaps. This tool bridges that gap with AI-powered analysis.

## ✨ Key Features

- **🤖 AI-Powered Analysis**: DigitalOcean Gradient AI for intelligent vulnerability detection
- **⚡ Real-Time Scanning**: Analyze GitHub PRs instantly with comprehensive reports
- **📊 Advanced Risk Scoring**: Blended static + AI confidence scores with severity weighting
- **🔧 Remediation Suggestions**: Natural language recommendations with actionable fixes
- **🌐 Web Interface**: Professional UI with demo capabilities and batch processing
- **🔒 Enterprise Security**: Rate limiting, input validation, comprehensive error handling
- **📈 Data-Driven**: Quantitative evidence with 40+ PR analysis and statistical validation

## 🚀 Quick Start

### Prerequisites
- Python 3.11+
- DigitalOcean Gradient AI API key ([Get one here](https://cloud.digitalocean.com/))
- GitHub token (optional, for higher rate limits)

### Installation & Setup
```bash
# Clone repository
git clone https://github.com/codeturtle-ai/codeturtle.git
cd fastapi-security-agent

# Install dependencies
pip install -r requirements.txt

# Configure environment
cp .env.example .env
# Edit .env with your API keys

# Launch application
uvicorn src.main:app --reload
```

**Access the web interface at:** `http://localhost:8000/ui`

## 📖 Usage Examples

### Single PR Analysis
```bash
curl -X POST "http://localhost:8000/analyze" \
  -H "Content-Type: application/json" \
  -d '{"url": "https://github.com/tiangolo/fastapi/pull/1"}'
```

### Batch Analysis
```bash
curl -X POST "http://localhost:8000/scan" \
  -H "Content-Type: application/json" \
  -d '{"urls": ["https://github.com/tiangolo/fastapi/pull/1", "..."]}'
```

### Web Interface
Visit `/ui` for an interactive experience with forms and visual results.

## 🏗️ Architecture

```
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│   FastAPI App   │    │  Security Agent  │    │  AI + Analysis  │
│                 │    │                  │    │                 │
│ • REST API      │◄──►│ • Hybrid Engine  │◄──►│ • Gradient AI   │
│ • Rate Limiting │    │ • Multi-Agent    │    │ • AST Parser    │
│ • Web UI        │    │ • RAG KB         │    │ • GitHub API    │
└─────────────────┘    └──────────────────┘    └─────────────────┘
```

- **Frontend Layer**: FastAPI with Jinja2 templates (extensible to Next.js)
- **Core Engine**: SecurityAgent with AST analysis, AI integration, and scoring
- **AI Layer**: DigitalOcean Gradient AI with RAG knowledge base
- **Data Layer**: GitHub API integration with comprehensive error handling

## 📊 Evidence & Results

**Quantitative Analysis Results:**
- ✅ **40 PRs Analyzed** from FastAPI repository
- ✅ **45 Vulnerabilities Detected** with statistical validation
- ✅ **90% Success Rate** in automated analysis
- ✅ **Risk Distribution**: 37% Low, 33% Medium, 30% High/Critical

**Key Findings:**
- Most common: SQL Injection (35%), Hardcoded Secrets (28%), Missing Auth (20%)
- Average risk score: 0.58 (Medium threat level)
- 12 high-risk PRs identified with actionable recommendations

**Evidence Package:**
- [Analysis Results CSV](data/analysis_results.csv)
- [Statistical Report](data/analysis_stats.json)
- [Evidence Documentation](data/evidence_report.md)

## 🔧 API Reference

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/` | GET | API information |
| `/health` | GET | Health check |
| `/analyze` | POST | Single PR analysis |
| `/scan` | POST | Batch PR analysis |
| `/report` | GET | Security reports |
| `/ui` | GET | Web interface |

## 🚀 Deployment

### Option 1: Vercel (Recommended)
```bash
npm install -g vercel
vercel --prod
# Configure environment variables in Vercel dashboard
```

### Option 2: DigitalOcean App Platform
```bash
# Use provided Dockerfile and .do/app.yaml
# Deploy via DigitalOcean dashboard
```

### Option 3: Local/Docker
```bash
docker build -t fastapi-security-agent .
docker run -p 8000:8000 fastapi-security-agent
```

## 🤝 Contributing

We welcome contributions! See [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

**Development Setup:**
```bash
# Install dev dependencies
pip install -r requirements.txt
pip install pytest mypy black

# Run tests
pytest tests/

# Code quality
mypy src/
black src/
```

## 📈 Roadmap

- [ ] Next.js frontend for enhanced UX
- [ ] Integration with GitHub Actions
- [ ] Support for additional frameworks
- [ ] Advanced vulnerability patterns
- [ ] Team collaboration features

## 🏆 Hacktoberfest 2025

This project was built for Hacktoberfest 2025, demonstrating:
- **Best Use of AI Platform**: DigitalOcean Gradient AI integration
- **Most Impactful**: Real security value for FastAPI developers
- **Best Overall**: Production-quality code with comprehensive testing

## 📄 License

MIT License - see [LICENSE](LICENSE) for details.

## 🙏 Acknowledgments

- **DigitalOcean** for Gradient AI Platform
- **FastAPI Community** for the amazing framework
- **Hacktoberfest** for the inspiration
- Built with ❤️ during Hacktoberfest 2025

---

**Ready to secure your FastAPI applications?** Star this repo and start analyzing PRs today! ⭐