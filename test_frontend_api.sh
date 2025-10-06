#!/bin/bash

# Frontend API Test Script
echo "🔧 Testing Frontend API Integration"
echo "==================================="

# Test CORS and API connectivity from frontend perspective
echo "📡 Testing CORS and API connectivity..."

# Test 1: Check if frontend can reach backend
echo "1. Testing backend connectivity from frontend perspective..."
response=$(curl -s -H "Origin: http://localhost:3000" "http://localhost:8000/health")
echo "   Response: $response"

# Test 2: Test preflight CORS for upload
echo "2. Testing CORS preflight for upload..."
cors_response=$(curl -s -o /dev/null -w "%{http_code}" \
  -H "Origin: http://localhost:3000" \
  -H "Access-Control-Request-Method: POST" \
  -H "Access-Control-Request-Headers: Content-Type" \
  -X OPTIONS "http://localhost:8000/api/upload")
echo "   CORS Status: $cors_response"

# Test 3: Test jobs endpoint with CORS
echo "3. Testing jobs endpoint with CORS headers..."
jobs_response=$(curl -s -H "Origin: http://localhost:3000" "http://localhost:8000/api/jobs")
echo "   Jobs count: $(echo "$jobs_response" | jq '. | length')"

# Test 4: Test individual status endpoint
echo "4. Testing status endpoint..."
task_id=$(echo "$jobs_response" | jq -r '.[0].task_id')
if [ "$task_id" != "null" ]; then
    status_response=$(curl -s -H "Origin: http://localhost:3000" "http://localhost:8000/api/status/$task_id")
    echo "   Status for $task_id: $(echo "$status_response" | jq -r '.status')"
else
    echo "   No jobs available for status test"
fi

echo ""
echo "🎯 Frontend API Integration Summary:"
echo "===================================="
if [ "$cors_response" = "200" ]; then
    echo "✅ CORS: Working correctly"
else
    echo "❌ CORS: Issues detected (code: $cors_response)"
fi

if [ -n "$response" ] && [ "$response" != "null" ]; then
    echo "✅ Backend connectivity: Working"
else
    echo "❌ Backend connectivity: Issues detected"
fi

echo ""
echo "💡 If you're still seeing frontend errors:"
echo "   1. Clear browser cache and reload"
echo "   2. Check browser console for detailed errors"
echo "   3. Ensure both servers are running:"
echo "      - Frontend: http://localhost:3000"
echo "      - Backend:  http://localhost:8000"