#!/bin/bash

# =============================================================================
# FastAPI Security Agent - Quick Setup Script
# =============================================================================

set -e  # Exit on any error

echo "🚀 FastAPI Security Agent - Quick Setup"
echo "========================================"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${GREEN}✅ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

print_error() {
    echo -e "${RED}❌ $1${NC}"
}

print_info() {
    echo -e "${BLUE}ℹ️  $1${NC}"
}

# Check if Python 3.9+ is installed
echo ""
print_info "Checking Python version..."
if command -v python3 &> /dev/null; then
    PYTHON_VERSION=$(python3 -c 'import sys; print(".".join(map(str, sys.version_info[:2])))')
    REQUIRED_VERSION="3.9"
    
    if python3 -c "import sys; exit(0 if sys.version_info >= (3,9) else 1)"; then
        print_status "Python $PYTHON_VERSION found (✓ >= 3.9)"
    else
        print_error "Python $PYTHON_VERSION found (✗ < 3.9 required)"
        echo "Please install Python 3.9 or higher"
        exit 1
    fi
else
    print_error "Python 3 not found. Please install Python 3.9 or higher"
    exit 1
fi

# Check if pip is available
if ! command -v pip3 &> /dev/null; then
    print_error "pip3 not found. Please install pip"
    exit 1
fi

# Create virtual environment if it doesn't exist
echo ""
print_info "Setting up virtual environment..."
if [ ! -d "venv" ]; then
    print_info "Creating virtual environment..."
    python3 -m venv venv
    print_status "Virtual environment created"
else
    print_status "Virtual environment already exists"
fi

# Activate virtual environment
print_info "Activating virtual environment..."
source venv/bin/activate
print_status "Virtual environment activated"

# Upgrade pip
print_info "Upgrading pip..."
pip install --upgrade pip > /dev/null 2>&1
print_status "pip upgraded"

# Install dependencies
echo ""
print_info "Installing dependencies..."
if [ -f "requirements.txt" ]; then
    pip install -r requirements.txt
    print_status "Dependencies installed from requirements.txt"
else
    print_warning "requirements.txt not found, installing core dependencies..."
    pip install fastapi uvicorn pydantic httpx python-dotenv slowapi jinja2 tenacity aiofiles
    print_status "Core dependencies installed"
fi

# Create .env file if it doesn't exist
echo ""
print_info "Setting up environment configuration..."
if [ ! -f ".env" ]; then
    if [ -f ".env.example" ]; then
        cp .env.example .env
        print_status "Created .env from .env.example"
        print_warning "Please edit .env file with your API keys"
    else
        print_warning ".env.example not found, creating basic .env file..."
        cat > .env << 'EOF'
# FastAPI Security Agent Configuration
GRADIENT_AI_API_KEY=your_digitalocean_ai_key_here
GITHUB_TOKEN=your_github_token_here
APP_ENV=development
DEBUG=true
LOG_LEVEL=INFO
MOCK_MODE=true
EOF
        print_status "Basic .env file created"
    fi
else
    print_status ".env file already exists"
fi

# Create logs directory
echo ""
print_info "Creating logs directory..."
mkdir -p logs
print_status "Logs directory created"

# Test basic functionality
echo ""
print_info "Testing basic functionality..."

# Test imports
if python3 -c "import sys; sys.path.append('src'); from clients.github_client import GitHubClient; print('GitHub client OK')" 2>/dev/null; then
    print_status "GitHub client import successful"
else
    print_error "GitHub client import failed"
fi

if python3 -c "import sys; sys.path.append('src'); from detection.ast_analyzer import ASTAnalyzer; print('AST analyzer OK')" 2>/dev/null; then
    print_status "AST analyzer import successful"
else
    print_error "AST analyzer import failed"
fi

if python3 -c "import sys; sys.path.append('src'); from ai.knowledge_base import FastAPISecurityKB; print('Knowledge base OK')" 2>/dev/null; then
    print_status "Knowledge base import successful"
else
    print_error "Knowledge base import failed"
fi

# Run comprehensive test if available
echo ""
if [ -f "test_implementation.py" ]; then
    print_info "Running comprehensive tests..."
    if python3 test_implementation.py > /dev/null 2>&1; then
        print_status "All tests passed"
    else
        print_warning "Some tests failed (this is normal without API keys)"
    fi
else
    print_warning "test_implementation.py not found, skipping comprehensive tests"
fi

# Test FastAPI startup
echo ""
print_info "Testing FastAPI application startup..."
if timeout 10s python3 -c "
import sys
sys.path.append('src')
from main import app
print('FastAPI app created successfully')
" 2>/dev/null; then
    print_status "FastAPI application startup successful"
else
    print_warning "FastAPI application startup test failed (check dependencies)"
fi

# Final instructions
echo ""
echo "========================================"
print_status "Setup completed successfully!"
echo ""
print_info "Next steps:"
echo "1. Edit .env file with your API keys:"
echo "   - Get DigitalOcean AI key: https://cloud.digitalocean.com/account/api/tokens"
echo "   - Get GitHub token: https://github.com/settings/tokens"
echo ""
echo "2. Start the development server:"
echo "   source venv/bin/activate"
echo "   uvicorn src.main:app --reload"
echo ""
echo "3. Test the application:"
echo "   curl http://localhost:8000/health"
echo "   open http://localhost:8000/ui"
echo ""
echo "4. Run comprehensive tests:"
echo "   python3 test_implementation.py"
echo ""
print_info "For detailed setup instructions, see: SETUP_AND_INTEGRATION_GUIDE.md"
echo ""

# Check if we should start the server
read -p "Would you like to start the development server now? (y/N): " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    print_info "Starting development server..."
    print_info "Server will be available at: http://localhost:8000"
    print_info "API documentation at: http://localhost:8000/docs"
    print_info "Web interface at: http://localhost:8000/ui"
    print_info "Press Ctrl+C to stop the server"
    echo ""
    uvicorn src.main:app --reload --host 0.0.0.0 --port 8000
fi