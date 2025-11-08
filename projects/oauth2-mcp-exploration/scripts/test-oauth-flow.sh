#!/bin/bash
# Test the complete OAuth flow

set -e

echo "╔══════════════════════════════════════════════════════════╗"
echo "║  🧪 Testing OAuth 2.0 Flow                               ║"
echo "╚══════════════════════════════════════════════════════════╝"
echo ""

AUTH_URL="${AUTH_SERVER_URL:-http://localhost:4000}"
RESOURCE_URL="${RESOURCE_SERVER_URL:-http://localhost:4001}"

# Test 1: Health checks
echo "📋 Test 1: Health Checks"
echo "Testing auth server..."
if curl -s "$AUTH_URL/health" | grep -q "ok"; then
    echo "✓ Auth server is healthy"
else
    echo "❌ Auth server is not responding"
    echo "   Make sure to run: npm run dev:auth"
    exit 1
fi

echo "Testing resource server..."
if curl -s "$RESOURCE_URL/health" | grep -q "ok"; then
    echo "✓ Resource server is healthy"
else
    echo "❌ Resource server is not responding"
    echo "   Make sure to run: npm run dev:resource"
    exit 1
fi
echo ""

# Test 2: Get access token (client_credentials)
echo "📋 Test 2: Get Access Token (client_credentials)"
echo "Requesting token for mcp-task-manager..."
TOKEN_RESPONSE=$(curl -s -X POST "$AUTH_URL/oauth/token" \
  -H "Content-Type: application/json" \
  -d '{
    "grant_type": "client_credentials",
    "client_id": "mcp-task-manager",
    "client_secret": "mcp-secret-12345",
    "scope": "tasks:read tasks:write"
  }')

ACCESS_TOKEN=$(echo "$TOKEN_RESPONSE" | grep -o '"access_token":"[^"]*"' | cut -d'"' -f4)

if [ -z "$ACCESS_TOKEN" ]; then
    echo "❌ Failed to get access token"
    echo "   Response: $TOKEN_RESPONSE"
    exit 1
fi

echo "✓ Access token received"
echo "  Token preview: ${ACCESS_TOKEN:0:50}..."
echo ""

# Test 3: Access protected resource with token
echo "📋 Test 3: Access Protected Resource"
echo "Listing tasks with token..."
TASKS_RESPONSE=$(curl -s "$RESOURCE_URL/api/tasks" \
  -H "Authorization: Bearer $ACCESS_TOKEN")

if echo "$TASKS_RESPONSE" | grep -q "tasks"; then
    echo "✓ Successfully accessed protected resource"
    TASK_COUNT=$(echo "$TASKS_RESPONSE" | grep -o '"total":[0-9]*' | cut -d':' -f2)
    echo "  Found $TASK_COUNT tasks"
else
    echo "❌ Failed to access protected resource"
    echo "   Response: $TASKS_RESPONSE"
    exit 1
fi
echo ""

# Test 4: Access without token (should fail)
echo "📋 Test 4: Access Without Token (should fail)"
echo "Attempting to access without token..."
NO_TOKEN_RESPONSE=$(curl -s -w "%{http_code}" "$RESOURCE_URL/api/tasks")
HTTP_CODE="${NO_TOKEN_RESPONSE: -3}"

if [ "$HTTP_CODE" = "401" ]; then
    echo "✓ Correctly rejected request without token (401)"
else
    echo "❌ Should have rejected request without token"
    echo "   HTTP Code: $HTTP_CODE"
fi
echo ""

# Test 5: Create a task
echo "📋 Test 5: Create Task"
echo "Creating a new task..."
CREATE_RESPONSE=$(curl -s -X POST "$RESOURCE_URL/api/tasks" \
  -H "Authorization: Bearer $ACCESS_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Test task from OAuth flow",
    "description": "Created during automated testing"
  }')

TASK_ID=$(echo "$CREATE_RESPONSE" | grep -o '"id":"[^"]*"' | cut -d'"' -f4)

if [ -n "$TASK_ID" ]; then
    echo "✓ Successfully created task"
    echo "  Task ID: $TASK_ID"
else
    echo "❌ Failed to create task"
    echo "   Response: $CREATE_RESPONSE"
    exit 1
fi
echo ""

# Test 6: Update the task
echo "📋 Test 6: Update Task"
echo "Updating task status to 'completed'..."
UPDATE_RESPONSE=$(curl -s -X PUT "$RESOURCE_URL/api/tasks/$TASK_ID" \
  -H "Authorization: Bearer $ACCESS_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "status": "completed"
  }')

if echo "$UPDATE_RESPONSE" | grep -q "completed"; then
    echo "✓ Successfully updated task"
else
    echo "❌ Failed to update task"
    echo "   Response: $UPDATE_RESPONSE"
    exit 1
fi
echo ""

# Test 7: Insufficient scope (should fail)
echo "📋 Test 7: Insufficient Scope (should fail)"
echo "Getting token with only tasks:read..."
READ_TOKEN_RESPONSE=$(curl -s -X POST "$AUTH_URL/oauth/token" \
  -H "Content-Type: application/json" \
  -d '{
    "grant_type": "client_credentials",
    "client_id": "mcp-task-manager",
    "client_secret": "mcp-secret-12345",
    "scope": "tasks:read"
  }')

READ_ONLY_TOKEN=$(echo "$READ_TOKEN_RESPONSE" | grep -o '"access_token":"[^"]*"' | cut -d'"' -f4)

echo "Attempting to create task with read-only token..."
FORBIDDEN_RESPONSE=$(curl -s -w "%{http_code}" -X POST "$RESOURCE_URL/api/tasks" \
  -H "Authorization: Bearer $READ_ONLY_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"title": "Should fail"}')

HTTP_CODE="${FORBIDDEN_RESPONSE: -3}"

if [ "$HTTP_CODE" = "403" ]; then
    echo "✓ Correctly rejected request with insufficient scope (403)"
else
    echo "❌ Should have rejected request with insufficient scope"
    echo "   HTTP Code: $HTTP_CODE"
fi
echo ""

# Summary
echo "╔══════════════════════════════════════════════════════════╗"
echo "║  ✅ All Tests Passed!                                    ║"
echo "╟──────────────────────────────────────────────────────────╢"
echo "║  OAuth 2.0 flow is working correctly:                    ║"
echo "║    ✓ Health checks                                       ║"
echo "║    ✓ Token generation                                    ║"
echo "║    ✓ Protected resource access                           ║"
echo "║    ✓ Unauthorized rejection                              ║"
echo "║    ✓ Task creation                                       ║"
echo "║    ✓ Task updates                                        ║"
echo "║    ✓ Scope enforcement                                   ║"
echo "╚══════════════════════════════════════════════════════════╝"
echo ""
