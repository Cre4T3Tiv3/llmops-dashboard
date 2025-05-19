#!/bin/bash
# scripts/simulate_llm_traffic.sh

# Generate valid JWT token directly in script
TOKEN=$(python3 -c "
import jwt, datetime
print(jwt.encode(
  {'sub': 'demo-user', 'exp': datetime.datetime.utcnow() + datetime.timedelta(minutes=5)},
  'supersecretkey',
  algorithm='HS256'
))")

# # Echo for confirmation
# echo "🪪 Using token:"
# echo "$TOKEN"
# echo ""

# Fire requests
for i in {1..25}; do
  curl -s -X POST http://localhost:8000/llm \
    -H "Authorization: Bearer $TOKEN" \
    -H "Content-Type: application/json" \
    -H "x-user-id: demo-user" \
    -d '{"prompt": "Explain entropy"}' >/dev/null
  echo "Request $i sent"
  sleep 0.5
done

echo "✅ 25 test requests completed. Check Grafana!"
