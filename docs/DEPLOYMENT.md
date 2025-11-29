# デプロイ手順書

## 概要

- **フロントエンド**: Vercel
- **バックエンド**: Google Cloud Run

---

## 1. フロントエンド (Vercel)

### 1.1 Vercel アカウント設定

1. [Vercel](https://vercel.com) にログイン
2. GitHub リポジトリを連携

### 1.2 プロジェクトインポート

1. 「Add New」→「Project」
2. リポジトリを選択
3. 設定:
   - **Framework Preset**: Vite
   - **Root Directory**: `frontend`
   - **Build Command**: `npm run build`
   - **Output Directory**: `dist`

### 1.3 環境変数設定

| 変数名 | 値 | 説明 |
|--------|-----|------|
| `VITE_API_URL` | `https://[YOUR-CLOUD-RUN-URL]` | バックエンドAPIのURL |

### 1.4 デプロイ

```bash
# 自動デプロイ: GitHubへのpushで自動実行
git push origin main
```

---

## 2. バックエンド (Cloud Run)

### 2.1 Google Cloud 設定

```bash
# プロジェクト設定
gcloud config set project YOUR_PROJECT_ID

# 必要なAPIを有効化
gcloud services enable run.googleapis.com
gcloud services enable cloudbuild.googleapis.com
gcloud services enable containerregistry.googleapis.com
```

### 2.2 環境変数（シークレット）設定

```bash
# Secret Manager でシークレットを作成
gcloud secrets create gemini-api-key --data-file=- <<< "YOUR_GEMINI_API_KEY"
gcloud secrets create openai-api-key --data-file=- <<< "YOUR_OPENAI_API_KEY"
```

### 2.3 デプロイ方法

#### 方法A: Cloud Build（推奨）

```bash
cd backend
gcloud builds submit --config=cloudbuild.yaml
```

#### 方法B: 手動デプロイ

```bash
cd backend

# イメージをビルド
gcloud builds submit --tag gcr.io/YOUR_PROJECT_ID/meta-ad-checker-api

# Cloud Run にデプロイ
gcloud run deploy meta-ad-checker-api \
  --image gcr.io/YOUR_PROJECT_ID/meta-ad-checker-api \
  --region asia-northeast1 \
  --platform managed \
  --allow-unauthenticated \
  --memory 512Mi \
  --cpu 1 \
  --timeout 60s \
  --set-secrets "GEMINI_API_KEY=gemini-api-key:latest,OPENAI_API_KEY=openai-api-key:latest"
```

### 2.4 CORS設定の更新

Cloud Run のURLが発行されたら、`backend/src/main.py` の CORS設定を更新:

```python
origins = [
    "http://localhost:3247",
    "https://your-app.vercel.app",  # Vercel のURL
]
```

---

## 3. デプロイ後の確認

### 3.1 ヘルスチェック

```bash
# バックエンド
curl https://[YOUR-CLOUD-RUN-URL]/api/health

# 期待されるレスポンス
{"status":"healthy","timestamp":"..."}
```

### 3.2 フロントエンド動作確認

1. Vercel のURLにアクセス
2. 広告テキストを入力
3. 「AIチェック実行」をクリック
4. 結果が表示されることを確認

---

## 4. 料金目安（無料枠内）

| サービス | 無料枠 | 想定使用量 |
|----------|--------|------------|
| Vercel | 月100GB転送 | 低（静的サイト） |
| Cloud Run | 月200万リクエスト | 低（個人利用） |
| Gemini API | 月45,000回 | 中（主要機能） |
| OpenAI Moderation | 無制限 | 低（補助機能） |

---

## 5. トラブルシューティング

### バックエンドに接続できない

1. Cloud Run のログを確認
2. CORS設定を確認
3. 環境変数（シークレット）を確認

### APIエラーが発生

1. Gemini API の利用制限を確認（15回/分）
2. APIキーの有効性を確認
3. レート制限の待機

---

最終更新: 2025-11-29
