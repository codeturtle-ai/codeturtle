#!/bin/bash

# =============================================================================
# FastAPI Security Agent - API Endpoint Testing Script
# =============================================================================

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
BASE_URL="http://localhost:8000"
TIMEOUT=30

# Function to print colored output
print_test() {
    echo -e "${BLUE}🧪 Testing: $1${NC}"
}

print_success() {
    echo -e "${GREEN}✅ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

print_error() {
    echo -e "${RED}❌ $1${NC}"
}

# Function to test HTTP endpoint
test_endpoint() {
    local method=$1
    local endpoint=$2
    local data=$3
    local expected_status=$4
    
    print_test "$method $endpoint"
    
    if [ -n "$data" ]; then
        response=$(curl -s -w "\n%{http_code}" -X "$method" \
                       -H "Content-Type: application/json" \
                       -d "$data" \
                       --max-time $TIMEOUT \
                       "$BASE_URL$endpoint" 2>/dev/null)
    else
        response=$(curl -s -w "\n%{http_code}" -X "$method" \
                       --max-time $TIMEOUT \
                       "$BASE_URL$endpoint" 2>/dev/null)
    fi
    
    if [ $? -eq 0 ]; then
        status_code=$(echo "$response" | tail -n1)
        body=$(echo "$response" | head -n -1)
        
        if [ "$status_code" = "$expected_status" ]; then
            print_success "Status: $status_code (Expected: $expected_status)"
            if [ ${#body} -gt 100 ]; then
                echo "Response: ${body:0:100}..."
            else
                echo "Response: $body"
            fi
        else
            print_error "Status: $status_code (Expected: $expected_status)"
            echo "Response: $body"
        fi
    else
        print_error "Request failed (timeout or connection error)"
    fi
    echo ""
}

# Check if server is running
echo "🚀 FastAPI Security Agent - API Endpoint Tests"
echo "=============================================="
echo ""

print_test "Checking if server is running at $BASE_URL"
if curl -s --max-time 5 "$BASE_URL/health" > /dev/null 2>&1; then
    print_success "Server is running"
else
    print_error "Server is not running at $BASE_URL"
    echo ""
    echo "Please start the server first:"
    echo "  uvicorn src.main:app --reload --host 0.0.0.0 --port 8000"
    echo ""
    exit 1
fi
echo ""

# Test basic endpoints
echo "📋 Testing Basic Endpoints"
echo "=========================="

# Health check
test_endpoint "GET" "/health" "" "200"

# Root endpoint
test_endpoint "GET" "/" "" "200"

# Web UI
test_endpoint "GET" "/ui" "" "200"

# Report endpoint
test_endpoint "GET" "/report" "" "200"

# Test API endpoints
echo "🔍 Testing Analysis Endpoints"
echo "============================="

# Test analyze endpoint with valid PR
test_endpoint "POST" "/analyze" '{"url": "https://github.com/tiangolo/fastapi/pull/1"}' "200"

# Test analyze endpoint with invalid URL
test_endpoint "POST" "/analyze" '{"url": "invalid-url"}' "422"

# Test batch scan endpoint
test_endpoint "POST" "/scan" '["https://github.com/tiangolo/fastapi/pull/1"]' "200"

# Test with multiple PRs
test_endpoint "POST" "/scan" '[
    "https://github.com/tiangolo/fastapi/pull/1",
    "https://github.com/tiangolo/fastapi/pull/2"
]' "200"

# Test error handling
echo "🚨 Testing Error Handling"
echo "========================="

# Test with malformed JSON
print_test "POST /analyze with malformed JSON"
response=$(curl -s -w "\n%{http_code}" -X POST \
               -H "Content-Type: application/json" \
               -d '{"url": "https://github.com/test/repo/pull/1"' \
               --max-time $TIMEOUT \
               "$BASE_URL/analyze" 2>/dev/null)

if [ $? -eq 0 ]; then
    status_code=$(echo "$response" | tail -n1)
    if [ "$status_code" = "422" ] || [ "$status_code" = "400" ]; then
        print_success "Malformed JSON handled correctly (Status: $status_code)"
    else
        print_warning "Unexpected status for malformed JSON: $status_code"
    fi
else
    print_error "Request failed"
fi
echo ""

# Test rate limiting (if enabled)
echo "⏱️  Testing Rate Limiting"
echo "========================"

print_test "Multiple rapid requests to test rate limiting"
rate_limit_hit=false
for i in {1..15}; do
    response=$(curl -s -w "%{http_code}" -X GET \
                   --max-time 5 \
                   "$BASE_URL/health" 2>/dev/null)
    
    if [ "$response" = "429" ]; then
        rate_limit_hit=true
        break
    fi
    sleep 0.1
done

if [ "$rate_limit_hit" = true ]; then
    print_success "Rate limiting is working (HTTP 429 received)"
else
    print_warning "Rate limiting not triggered (may be disabled or limit not reached)"
fi
echo ""

# Test performance
echo "⚡ Performance Tests"
echo "==================="

print_test "Response time for health endpoint"
start_time=$(date +%s%N)
curl -s "$BASE_URL/health" > /dev/null 2>&1
end_time=$(date +%s%N)
duration=$(( (end_time - start_time) / 1000000 ))

if [ $duration -lt 1000 ]; then
    print_success "Health endpoint response time: ${duration}ms (< 1000ms)"
else
    print_warning "Health endpoint response time: ${duration}ms (>= 1000ms)"
fi
echo ""

print_test "Response time for analyze endpoint"
start_time=$(date +%s%N)
curl -s -X POST \
     -H "Content-Type: application/json" \
     -d '{"url": "https://github.com/tiangolo/fastapi/pull/1"}' \
     "$BASE_URL/analyze" > /dev/null 2>&1
end_time=$(date +%s%N)
duration=$(( (end_time - start_time) / 1000000 ))

if [ $duration -lt 30000 ]; then
    print_success "Analyze endpoint response time: ${duration}ms (< 30s)"
else
    print_warning "Analyze endpoint response time: ${duration}ms (>= 30s)"
fi
echo ""

# Test with real vulnerability code
echo "🔍 Testing Vulnerability Detection"
echo "=================================="

print_test "Testing with code containing vulnerabilities"

# Create a test PR analysis request
vulnerability_test='{"url": "https://github.com/tiangolo/fastapi/pull/1"}'

response=$(curl -s -X POST \
               -H "Content-Type: application/json" \
               -d "$vulnerability_test" \
               --max-time 60 \
               "$BASE_URL/analyze" 2>/dev/null)

if [ $? -eq 0 ]; then
    # Check if response contains expected fields
    if echo "$response" | grep -q '"vulnerabilities"' && \
       echo "$response" | grep -q '"risk_score"' && \
       echo "$response" | grep -q '"recommendations"'; then
        print_success "Vulnerability analysis response contains expected fields"
        
        # Extract some basic info
        vuln_count=$(echo "$response" | grep -o '"vulnerabilities":\[[^]]*\]' | grep -o ',' | wc -l)
        vuln_count=$((vuln_count + 1))
        
        if echo "$response" | grep -q '"vulnerabilities":\[\]'; then
            vuln_count=0
        fi
        
        echo "  Vulnerabilities found: $vuln_count"
        
        # Extract risk score if possible
        if echo "$response" | grep -q '"risk_score":[0-9.]*'; then
            risk_score=$(echo "$response" | grep -o '"risk_score":[0-9.]*' | cut -d':' -f2)
            echo "  Risk score: $risk_score"
        fi
        
    else
        print_warning "Response missing expected fields"
        echo "Response: ${response:0:200}..."
    fi
else
    print_error "Vulnerability analysis request failed"
fi
echo ""

# Summary
echo "📊 Test Summary"
echo "==============="
echo ""
print_success "API endpoint testing completed!"
echo ""
echo "If any tests failed, check:"
echo "1. Server is running: uvicorn src.main:app --reload"
echo "2. Environment variables are set in .env file"
echo "3. Dependencies are installed: pip install -r requirements.txt"
echo "4. Check server logs for detailed error messages"
echo ""
echo "For more detailed testing, run:"
echo "  python3 test_implementation.py"
echo ""
echo "API Documentation available at:"
echo "  $BASE_URL/docs"
echo ""
echo "Web Interface available at:"
echo "  $BASE_URL/ui"