#!/usr/bin/env python3
"""Test API keys configuration."""

import os
import sys

def test_gradient_ai_key():
    """Test DigitalOcean Gradient AI key."""
    # Try to load dotenv if available
    try:
        from dotenv import load_dotenv
        load_dotenv()
    except ImportError:
        print("⚠️  python-dotenv not installed, reading from environment only")
    
    api_key = os.getenv("GRADIENT_AI_API_KEY")
    
    if not api_key:
        print("❌ GRADIENT_AI_API_KEY not found in environment or .env file")
        print("   Create .env file with: GRADIENT_AI_API_KEY=your_token_here")
        return False
    
    if api_key == "your_digitalocean_token_here":
        print("⚠️  GRADIENT_AI_API_KEY still has placeholder value")
        print("   Replace with your actual DigitalOcean API token")
        return False
    
    if len(api_key) < 20:
        print(f"⚠️  GRADIENT_AI_API_KEY seems too short (got: {len(api_key)} chars)")
        print("   DigitalOcean tokens are typically 64+ characters")
        return False
    
    # Show masked token
    masked = api_key[:15] + "..." + api_key[-4:] if len(api_key) > 19 else api_key[:10] + "..."
    print(f"✅ GRADIENT_AI_API_KEY configured: {masked}")
    print(f"   Length: {len(api_key)} characters")
    return True

def test_github_token():
    """Test GitHub token."""
    try:
        from dotenv import load_dotenv
        load_dotenv()
    except ImportError:
        pass
    
    token = os.getenv("GITHUB_TOKEN")
    
    if not token:
        print("⚠️  GITHUB_TOKEN not found (optional but recommended)")
        print("   Without it, GitHub API is limited to 60 requests/hour")
        print("   With it, you get 5000 requests/hour")
        return True  # Optional, so not a failure
    
    if token == "your_github_token_here":
        print("⚠️  GITHUB_TOKEN still has placeholder value")
        print("   Replace with your actual GitHub Personal Access Token")
        return True  # Optional
    
    if len(token) < 20:
        print(f"⚠️  GITHUB_TOKEN seems too short (got: {len(token)} chars)")
        return True  # Optional
    
    masked = token[:10] + "..." + token[-4:] if len(token) > 14 else token[:8] + "..."
    print(f"✅ GITHUB_TOKEN configured: {masked}")
    print(f"   Length: {len(token)} characters")
    return True

def check_env_file():
    """Check if .env file exists."""
    if os.path.exists('.env'):
        print("✅ .env file found")
        return True
    else:
        print("⚠️  .env file not found")
        print("   Copy .env.example to .env and add your tokens:")
        print("   cp .env.example .env")
        return False

def main():
    print("=" * 70)
    print("FastAPI Security Agent - API Keys Configuration Test")
    print("=" * 70)
    print()
    
    # Check .env file
    print("📁 Checking environment file...")
    env_exists = check_env_file()
    print()
    
    # Test API keys
    print("🔑 Testing API keys...")
    gradient_ok = test_gradient_ai_key()
    print()
    github_ok = test_github_token()
    
    print()
    print("=" * 70)
    
    if gradient_ok and github_ok:
        print("✅ Configuration complete! All API keys ready.")
        print()
        print("📋 Next steps:")
        print()
        print("1. Install dependencies:")
        print("   pip install -r requirements.txt")
        print()
        print("2. Start the application:")
        print("   uvicorn src.main:app --reload")
        print()
        print("3. Test the health endpoint:")
        print("   curl http://localhost:8000/health")
        print()
        print("4. Analyze a PR:")
        print("   curl -X POST http://localhost:8000/analyze \\")
        print("     -H 'Content-Type: application/json' \\")
        print("     -d '{\"url\": \"https://github.com/tiangolo/fastapi/pull/1\"}'")
        print()
        return 0
    else:
        print("❌ Configuration incomplete")
        print()
        print("📋 Required actions:")
        print()
        if not env_exists:
            print("1. Create .env file:")
            print("   cp .env.example .env")
            print()
        if not gradient_ok:
            print("2. Add DigitalOcean API token to .env:")
            print("   GRADIENT_AI_API_KEY=your_actual_token_here")
            print()
            print("   Get token at: https://cloud.digitalocean.com/account/api/tokens")
            print()
        if not github_ok and not os.getenv("GITHUB_TOKEN"):
            print("3. (Optional) Add GitHub token to .env for higher rate limits:")
            print("   GITHUB_TOKEN=your_github_token_here")
            print()
            print("   Get token at: https://github.com/settings/tokens")
            print()
        
        print("See GRADIENT_AI_SETUP_GUIDE.md for detailed instructions.")
        print()
        return 1

if __name__ == "__main__":
    sys.exit(main())
