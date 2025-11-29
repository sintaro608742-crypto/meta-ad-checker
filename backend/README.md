# メタ広告審査チェッカー - バックエンド

Meta広告の審査基準に基づいた事前チェックツールのバックエンドAPI

## 技術スタック

- **Python**: 3.11+
- **フレームワーク**: FastAPI
- **バリデーション**: Pydantic v2
- **画像処理**: Pillow
- **AI API**: Google Gemini 2.5 Flash, OpenAI (オプション)

## プロジェクト構造

```
backend/
├── src/
│   ├── main.py              # FastAPIアプリケーション
│   ├── types.py             # Pydantic型定義
│   ├── __init__.py
│   ├── utils/
│   │   ├── __init__.py
│   │   ├── errors.py        # エラーハンドリング
│   │   ├── image.py         # 画像処理ユーティリティ
│   │   └── logger.py        # ロギング設定
│   └── routes/
│       └── __init__.py      # ルートモジュール（スライス1-A/1-Bで実装予定）
├── tests/
│   └── integration/
├── requirements.txt         # 依存関係
├── .env.example            # 環境変数サンプル
├── .env.local              # 環境変数（.gitignoreに追加）
└── README.md               # このファイル
```

## セットアップ

### 1. Python仮想環境の作成

```bash
cd backend
python3 -m venv venv
source venv/bin/activate  # macOS/Linux
# または
venv\Scripts\activate  # Windows
```

### 2. 依存関係のインストール

```bash
pip install -r requirements.txt
```

### 3. 環境変数の設定

`.env.example`をコピーして`.env.local`を作成:

```bash
cp .env.example .env.local
```

`.env.local`を編集して必要な環境変数を設定:

```env
PORT=8432
ENVIRONMENT=development
LOG_LEVEL=INFO
ALLOWED_ORIGINS=http://localhost:3247,http://127.0.0.1:3247
GEMINI_API_KEY=your_gemini_api_key_here
OPENAI_API_KEY=your_openai_api_key_here  # オプション
```

## 実行

### 開発モード（ホットリロード有効）

```bash
# 方法1: Pythonモジュールとして実行
python -m uvicorn src.main:app --reload --port 8432

# 方法2: main.pyを直接実行
cd src
python main.py
```

### 本番モード

```bash
python -m uvicorn src.main:app --host 0.0.0.0 --port 8432
```

## API ドキュメント

サーバー起動後、以下のURLでAPIドキュメントにアクセス可能:

- **Swagger UI**: http://localhost:8432/docs
- **ReDoc**: http://localhost:8432/redoc

## エンドポイント（予定）

| エンドポイント | メソッド | 説明 | 実装状況 |
|--------------|---------|------|---------|
| `/` | GET | ルートエンドポイント | ✅ |
| `/api/health` | GET | ヘルスチェック | スライス1-A |
| `/api/check` | POST | 広告審査AI判定 | スライス1-B |

## 型定義の同期

フロントエンド (`frontend/src/types/index.ts`) とバックエンド (`backend/src/types.py`) の型定義は完全に同期しています。

詳細は `TYPE_SYNC_VERIFICATION.md` を参照してください。

## 開発ルール

### エラーハンドリング

全てのエラーレスポンスは以下の形式:

```json
{
  "error": "error_type",
  "message": "ユーザー向けメッセージ",
  "details": {
    "additional": "info"
  }
}
```

### 画像処理

- **最大サイズ**: 20MB
- **対応形式**: JPEG, PNG, WebP
- **エンコード**: Base64

### ログレベル

- **DEBUG**: 詳細なデバッグ情報
- **INFO**: 一般的な情報（デフォルト）
- **WARNING**: 警告
- **ERROR**: エラー
- **CRITICAL**: 致命的なエラー

## テスト

```bash
# 単体テスト
pytest

# カバレッジ付き
pytest --cov=src --cov-report=html

# 統合テスト
pytest tests/integration
```

## デプロイ

### Google Cloud Run（予定）

1. Dockerイメージのビルド
2. Google Container Registryにプッシュ
3. Cloud Runにデプロイ

詳細は Phase 9（デプロイ準備）で実装予定。

## トラブルシューティング

### ポート8432が既に使用されている

```bash
# ポートを使用しているプロセスを確認
lsof -i :8432

# プロセスを終了
kill -9 <PID>
```

### Gemini APIエラー

- API キーが正しく設定されているか確認
- 無料枠の制限（月45,000回）を超えていないか確認
- レート制限（1分15リクエスト）を超えていないか確認

### 画像アップロードエラー

- ファイルサイズが20MB以下か確認
- 対応形式（JPEG/PNG/WebP）か確認
- Base64エンコードが正しいか確認

## 開発進捗

現在の実装状況は `docs/SCOPE_PROGRESS.md` の「セクション8: バックエンド実装計画」を参照してください。

### スライス0: 共通基盤（✅ 完了）

- [x] プロジェクト構造作成
- [x] 依存関係管理
- [x] FastAPIアプリケーション初期化
- [x] CORS設定
- [x] 環境変数管理
- [x] 型定義
- [x] エラーハンドリング
- [x] 画像処理ユーティリティ
- [x] バリデーション
- [x] ロギング設定

### スライス1-A: ヘルスチェック（未実装）

- [ ] `/api/health` エンドポイント実装

### スライス1-B: 広告審査AI判定（未実装）

- [ ] `/api/check` エンドポイント実装
- [ ] Gemini API連携
- [ ] OpenAI Moderation API連携（オプション）

## ライセンス

MIT

## 作成者

Claude Code

---

**最終更新日**: 2025-11-23
**バージョン**: 1.0（MVP - スライス0完了）
