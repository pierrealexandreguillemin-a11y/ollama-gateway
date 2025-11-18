#!/bin/bash
# Script de test complet du Ollama Gateway

echo "🧪 Test Suite - Ollama Gateway"
echo "=============================="
echo ""

# Test 1: Health Check
echo "1️⃣ Health Check..."
HEALTH=$(curl -s http://localhost:4000/health)
echo "$HEALTH" | python3 -m json.tool
echo ""

# Test 2: Routing - Code
echo "2️⃣ Routing Test - Code..."
ROUTE_CODE=$(curl -s -X POST http://localhost:4000/gateway/route \
  -H "Content-Type: application/json" \
  -d '{"prompt": "Write a JavaScript function"}')
echo "$ROUTE_CODE" | python3 -m json.tool
echo ""

# Test 3: Routing - Chess
echo "3️⃣ Routing Test - Chess..."
ROUTE_CHESS=$(curl -s -X POST http://localhost:4000/gateway/route \
  -H "Content-Type: application/json" \
  -d '{"prompt": "Explain the Ruy Lopez opening"}')
echo "$ROUTE_CHESS" | python3 -m json.tool
echo ""

# Test 4: Routing - Translation
echo "4️⃣ Routing Test - Translation..."
ROUTE_TRANS=$(curl -s -X POST http://localhost:4000/gateway/route \
  -H "Content-Type: application/json" \
  -d '{"prompt": "Translate to Spanish: Hello"}')
echo "$ROUTE_TRANS" | python3 -m json.tool
echo ""

# Test 5: Chat Completion
echo "5️⃣ Chat Completion Test..."
echo "Sending: Write Python code to add two numbers"
RESPONSE=$(curl -s -X POST http://localhost:4000/v1/chat/completions \
  -H "Content-Type: application/json" \
  -d '{
    "model": "auto",
    "messages": [
      {"role": "user", "content": "Write Python code to add two numbers. One line only."}
    ]
  }')

MODEL=$(echo "$RESPONSE" | python3 -c "import sys, json; print(json.load(sys.stdin)['model'])")
CONTENT=$(echo "$RESPONSE" | python3 -c "import sys, json; print(json.load(sys.stdin)['choices'][0]['message']['content'][:200])")

echo "Model selected: $MODEL"
echo "Response: $CONTENT..."
echo ""

# Test 6: List Models
echo "6️⃣ List Available Models..."
curl -s http://localhost:4000/v1/models | python3 -c "import sys, json; data=json.load(sys.stdin); print(f\"Total models: {len(data['data'])}\"); [print(f\"  - {m['id']} ({m['metadata']['role']})\") for m in data['data'][:5]]"
echo ""

echo "✅ All tests completed!"
echo ""
echo "Gateway is ready for:"
echo "  - Claude-Code integration"
echo "  - Continue.dev integration"
echo "  - Cursor integration"
echo ""
echo "Next: Configure your IDE with http://localhost:4000/v1"
