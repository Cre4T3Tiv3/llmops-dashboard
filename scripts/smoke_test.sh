#!/bin/bash
# smoke_test.sh

# Load token from environment or generate using hardcoded demo JWT secret
TOKEN=$(python3 -c "import jwt; print(jwt.encode({'sub': 'demo-user'}, 'supersecretkey', algorithm='HS256'))")

# # # Echo for confirmation
# echo "Generated JWT Token:"
# echo $TOKEN
# echo ""

# Send test LLM request
echo "Sending POST /llm request with prompt..."
RESPONSE=$(curl -s -X POST http://localhost:8000/llm \
    -H "Authorization: Bearer $TOKEN" \
    -H "Content-Type: application/json" \
    -d '{"prompt": "Test vector embeddings"}')

echo "LLM Response:"
echo $RESPONSE

# Display /metrics summary
echo ""
echo "Checking /metrics endpoint..."
curl -s http://localhost:8000/metrics | grep request_count || echo "Metrics not found."

# Show SQLite logs (if sqlite3 CLI is available)
if command -v sqlite3 &>/dev/null; then
    echo ""
    echo "Querying SQLite usage logs..."
    sqlite3 data/usage.db "SELECT * FROM usage_logs ORDER BY id DESC LIMIT 3;"
else
    echo "sqlite3 not installed, skipping DB check."
fi
