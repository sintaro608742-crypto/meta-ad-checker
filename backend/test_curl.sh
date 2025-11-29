#!/bin/bash

# Test /api/check endpoint
curl -X POST http://localhost:8432/api/check \
  -H "Content-Type: application/json" \
  -d '{"headline":"お得なキャンペーン実施中","description":"高品質な商品を提供しています。","cta":"詳細を見る"}'
