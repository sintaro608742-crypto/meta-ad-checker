#!/usr/bin/env python3
"""
Gemini APIの直接テスト
"""
import os
import google.generativeai as genai

# APIキーを設定
api_key = "AIzaSyB9Ne6eWaOSj_q7huNgeZIbamTuT50qHo8"
genai.configure(api_key=api_key)

# モデルを初期化
model = genai.GenerativeModel("gemini-2.0-flash-exp")

try:
    # テストプロンプト
    response = model.generate_content("Hello, please respond with 'API is working'")
    print("✓ API接続成功")
    print(f"Response: {response.text}")
except Exception as e:
    print(f"✗ API接続失敗: {str(e)}")
    print(f"Error type: {type(e).__name__}")
