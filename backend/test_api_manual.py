"""
手動APIテスト
"""

import sys
sys.path.insert(0, 'src')

from fastapi.testclient import TestClient
from src.main import app

client = TestClient(app)

# テスト1: バリデーションエラー
print("Test 1: Validation Error (no content)")
response = client.post("/api/check", json={})
print(f"Status: {response.status_code}")
print(f"Response: {response.json()}")
print()

# テスト2: テキストのみの審査
print("Test 2: Text-only check")
response = client.post("/api/check", json={
    "headline": "お得なキャンペーン実施中",
    "description": "高品質な商品を提供しています。",
    "cta": "詳細を見る"
})
print(f"Status: {response.status_code}")
if response.status_code == 200:
    data = response.json()
    print(f"Score: {data['overall_score']}")
    print(f"Status: {data['status']}")
    print(f"Confidence: {data['confidence']}")
    print(f"Violations: {len(data['violations'])}")
    print(f"API Used: {data['api_used']}")
else:
    print(f"Error: {response.json()}")
print()

# テスト3: 違反を含むテキスト
print("Test 3: Text with violations")
response = client.post("/api/check", json={
    "headline": "この薬を飲めば病気が治ります",
    "description": "100%保証！業界最安値で提供します。",
})
print(f"Status: {response.status_code}")
if response.status_code == 200:
    data = response.json()
    print(f"Score: {data['overall_score']}")
    print(f"Status: {data['status']}")
    print(f"Violations: {len(data['violations'])}")
    if data['violations']:
        print("Violation categories:", [v['category'] for v in data['violations']])
else:
    print(f"Error: {response.json()}")
