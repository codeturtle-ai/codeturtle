# FastAPI Security Agent

An AI-powered open-source tool for automated code vulnerability detection in FastAPI projects, leveraging DigitalOcean's Gradient AI Platform. This project transforms existing Magnet POC into a production-ready security scanner for GitHub PRs.

## Overview

FastAPI Security Agent analyzes code patterns in real-time using advanced AI to detect vulnerabilities such as:
- SSTI (Server-Side Template Injection)
- SQL Injection patterns
- Hardcoded secrets
- Missing error handling
- And more security issues

Built for Hacktoberfest 2025, this tool combines static analysis with AI insights to provide actionable security recommendations for developers.

## Features

- **AI-Powered Analysis**: Uses DigitalOcean Gradient AI for intelligent vulnerability detection
- **Real-Time Scanning**: Analyze GitHub PRs instantly
- **Risk Scoring**: Combines static and AI confidence scores
- **Remediation Suggestions**: AI-generated fixes and best practices
- **Web Interface**: Simple FastAPI-based UI for easy interaction
- **Open Source**: MIT licensed for community contribution

## Quick Start

### Prerequisites
- Python 3.11+
- DigitalOcean Gradient AI API key (get one at [DigitalOcean Console](https://cloud.digitalocean.com/))

### Installation
1. Clone the repository:
   ```bash
   git clone https://github.com/codeturtle-ai/codeturtle.git
   cd fastapi-security-agent
   ```

2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Set up environment variables:
   ```bash
   cp .env.example .env
   # Edit .env with your Gradient AI API key
   ```

4. Run the application:
   ```bash
   uvicorn src.main:app --reload
   ```

5. Access the web interface at `http://localhost:8000`

## Usage

### Analyze a PR
POST to `/analyze` with a GitHub PR URL:
```json
{
  "url": "https://github.com/example/repo/pull/123"
}
```

### Batch Scanning
Use `/scan` endpoint for multiple PRs.

## Architecture

- **Backend**: FastAPI with Python 3.11+
- **AI Integration**: DigitalOcean Gradient AI Platform
- **Analysis Engine**: AST-based static analysis + AI agent routing
- **Deployment**: Ready for DigitalOcean App Platform

## Contributing

We welcome contributions! Please see [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

## License

MIT License - see [LICENSE](LICENSE) file for details.

## Acknowledgments

Built during Hacktoberfest 2025 with DigitalOcean's Gradient AI Platform.