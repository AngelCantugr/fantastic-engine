#!/bin/bash
# Helper script to get an OAuth token

AUTH_URL="${AUTH_SERVER_URL:-http://localhost:4000}"
CLIENT_ID="${1:-mcp-task-manager}"
CLIENT_SECRET="${2:-mcp-secret-12345}"
SCOPE="${3:-tasks:read tasks:write}"

echo "🔑 Getting OAuth token..."
echo "   Client ID: $CLIENT_ID"
echo "   Scope: $SCOPE"
echo ""

RESPONSE=$(curl -s -X POST "$AUTH_URL/oauth/token" \
  -H "Content-Type: application/json" \
  -d "{
    \"grant_type\": \"client_credentials\",
    \"client_id\": \"$CLIENT_ID\",
    \"client_secret\": \"$CLIENT_SECRET\",
    \"scope\": \"$SCOPE\"
  }")

# Pretty print the response
echo "Response:"
echo "$RESPONSE" | jq '.'

# Extract and display token
TOKEN=$(echo "$RESPONSE" | jq -r '.access_token')

if [ "$TOKEN" != "null" ] && [ -n "$TOKEN" ]; then
    echo ""
    echo "✓ Access token (copy this for use in requests):"
    echo "export TOKEN='$TOKEN'"
    echo ""
    echo "Use it like this:"
    echo "curl http://localhost:4001/api/tasks -H \"Authorization: Bearer \$TOKEN\""
else
    echo ""
    echo "❌ Failed to get token"
    exit 1
fi
