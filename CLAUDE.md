# プロジェクト設定

## 基本設定
```yaml
プロジェクト名: メタ広告審査チェッカー
開始日: 2025-11-22
技術スタック:
  frontend:
    - React 18
    - TypeScript 5
    - MUI v6
    - Vite 5
    - React Router v6
    - Zustand
    - React Query
    - React Dropzone
  backend:
    - Python 3.11+
    - FastAPI
    - Pydantic v2
    - Pillow
    - google-generativeai
  database:
    - なし（MVPはステートレス）
    - 将来拡張: PostgreSQL (Neon)
  infrastructure:
    - Frontend: Vercel
    - Backend: Render
```

## デプロイ設定
```yaml
本番環境:
  frontend:
    - URL: https://meta-ad-checker.vercel.app
    - プラットフォーム: Vercel
    - 環境変数: VITE_API_URL
  backend:
    - URL: https://meta-ad-checker.onrender.com
    - プラットフォーム: Render
    - 環境変数: ALLOWED_ORIGINS, GEMINI_API_KEY
    - APIドキュメント: https://meta-ad-checker.onrender.com/docs

注意事項:
  - Render無料プランは15分間非アクティブでスリープ
  - 初回アクセス時は起動に50秒程度かかる場合あり
```

## 開発環境
```yaml
ポート設定:
  # 複数プロジェクト並行開発のため、一般的でないポートを使用
  frontend: 3247
  backend: 8432

環境変数:
  設定ファイル: .env.local（ルートディレクトリ）
  必須項目:
    - VITE_API_URL（フロントエンド用）
    - GEMINI_API_KEY（バックエンド用）
    - OPENAI_API_KEY（バックエンド用、オプション）
    - PORT（バックエンド用、デフォルト8432）
```

## テスト認証情報
```yaml
開発用アカウント:
  # MVPでは認証なし（パブリックアクセス）
  email: N/A
  password: N/A

外部サービス:
  Gemini API:
    - 無料枠: 月45,000回
    - 用途: テキスト+画像の審査AI判定
  OpenAI Moderation API:
    - 完全無料
    - 用途: 有害コンテンツ検出（補助）
```

## コーディング規約

### 命名規則
```yaml
ファイル名:
  - コンポーネント: PascalCase.tsx (例: AdChecker.tsx)
  - ユーティリティ: camelCase.ts (例: formatResult.ts)
  - 定数: UPPER_SNAKE_CASE.ts (例: API_ENDPOINTS.ts)
  - API Routes: kebab-case (例: /api/check)

変数・関数:
  - 変数: camelCase (例: adText, imageFile)
  - 関数: camelCase (例: checkAdvertisement)
  - 定数: UPPER_SNAKE_CASE (例: MAX_FILE_SIZE)
  - 型/インターフェース: PascalCase (例: AdCheckRequest, AdCheckResponse)
```

### コード品質
```yaml
必須ルール:
  - TypeScript: strictモード有効
  - 未使用の変数/import禁止
  - console.log本番環境禁止（開発環境のみ）
  - エラーハンドリング必須（特にAPI呼び出し）
  - 画像アップロードは最大20MB制限

フォーマット:
  - インデント: スペース2つ
  - セミコロン: あり
  - クォート: シングル（TypeScript/JavaScript）
  - 改行: LF（Unix形式）
```

## プロジェクト固有ルール

### APIエンドポイント
```yaml
命名規則:
  - RESTful形式を厳守
  - ケバブケース使用 (/api/check, /api/health)
  - バージョニング不要（MVP時）

エラーレスポンス:
  - 常にJSON形式
  - error, message, detailsフィールドを含む
  - HTTPステータスコードを適切に使用
    * 200: 成功
    * 400: バリデーションエラー
    * 429: レート制限超過
    * 500: サーバーエラー
    * 503: サービス利用不可
```

### 型定義
```yaml
配置:
  frontend: src/types/index.ts
  backend: src/types.py

同期ルール:
  - フロントとバックで型定義を一致させる
  - API Request/Responseは特に厳密に一致
  - 変更時は両方を同時に更新

主要型:
  - AdCheckRequest: テキスト+画像の入力
  - AdCheckResponse: AI審査結果
  - Violation: 違反項目
  - Recommendation: 改善提案
```

### AI API使用のベストプラクティス
```yaml
Gemini API:
  - タイムアウト: 30秒
  - リトライ: 最大3回（指数バックオフ）
  - エラーハンドリング:
    * 429（レート制限）: 待機してリトライ
    * 500（サーバーエラー）: リトライ
    * その他: ユーザーにエラーメッセージ表示
  - プロンプト設計:
    * メタ広告ポリシーを明示
    * JSON形式での返却を指定
    * 一貫性のためtemperature=0.3程度

画像処理:
  - base64エンコード必須
  - 最大20MB制限
  - 対応形式: JPEG, PNG, WebP
  - サイズ最適化を検討（必要に応じて）
```

## 🆕 最新技術情報（知識カットオフ対応）

### Meta広告審査の現状（2025年1月時点）
```yaml
重要な変更:
  - Text Overlay Tool廃止済み（2020年9月）
  - 20%ルールは厳密には撤廃されているが、アルゴリズムペナルティあり
  - 推奨: 画像内テキストは15%以下が最適
  - Meta公式の事前審査APIは存在しない
  - Ad Recommendation APIは限定的（完全な審査予測は不可）

審査基準（主要5項目）:
  1. テキストオーバーレイ（20%以下推奨）
  2. 禁止コンテンツ（アルコール、タバコ、医薬品等）
  3. 過度な肌露出・性的表現
  4. ビフォーアフター表現（ダイエット、美容）
  5. 誇大広告・誤解を招く表現

API仕様:
  - Marketing API v22.0が最新（2025年1月）
  - effective_statusでDISAPPROVED検出可能
  - ad_review_feedbackで不承認理由取得（一部広告のみ）
```

### AI API仕様（2025年1月時点）
```yaml
Google Gemini 2.5 Flash:
  - 料金: 入力$0.15/100万トークン、出力$0.60/100万トークン
  - 無料枠: 1分15リクエスト、1日1,500リクエスト
  - 画像処理: 1024x1024で約1,290トークン
  - レスポンス速度: 1-3秒
  - コンテキスト: 100万トークン

OpenAI GPT-4o:
  - 料金: 入力$5.00/100万トークン、出力$15.00/100万トークン
  - 画像処理: low-detail 85トークン、high-detail 約1,100トークン
  - Vision機能: テキスト+画像同時処理可能
  - OCR精度: 94.12%

OpenAI Moderation API:
  - 完全無料
  - GPT-4oベース
  - 6カテゴリ検出（性的、暴力、ヘイト、自傷、違法等）
```

### インフラ仕様（2025年1月時点）
```yaml
Vercel:
  - 無料枠: 月100GB転送、無制限デプロイ
  - React/Vite最適化
  - 自動HTTPS、CDN

Google Cloud Run:
  - 無料枠: 月200万リクエスト
  - 自動スケーリング
  - コンテナベース
  - コールドスタート: 通常1-2秒

Neon（PostgreSQL）:
  - 無料枠: 3プロジェクト、0.5GB
  - サーバーレス
  - 自動スケーリング
  - ブランチ機能あり
  - 注記: MVPでは不要（Phase 11拡張時）
```

## プロジェクト特有の注意事項

### セキュリティ
```yaml
API キー管理:
  - .env.localに保存（Gitにコミットしない）
  - .gitignoreに.env.localを追加
  - 本番環境: Vercel/Cloud Runの環境変数機能使用

画像アップロード:
  - ファイル形式検証必須
  - サイズ制限: 20MB
  - MIME type検証
  - 悪意のあるファイル対策

レート制限:
  - MVP時は実装不要（認証なし）
  - 将来的にIPベース制限検討
```

### パフォーマンス
```yaml
フロントエンド:
  - 画像プレビュー: FileReaderで即座表示
  - 結果表示: React Queryでキャッシュ
  - ローディング表示: 30秒以内に結果表示を保証

バックエンド:
  - 非同期処理: FastAPIのasync/await活用
  - タイムアウト: 30秒
  - 画像最適化: 必要に応じてリサイズ
```

### エラーハンドリング
```yaml
想定エラー:
  1. ファイルサイズ超過 → 400エラー、わかりやすいメッセージ
  2. 対応形式外 → 400エラー、対応形式を明示
  3. API呼び出し失敗 → リトライ、最大3回
  4. タイムアウト → 503エラー、再試行を促す
  5. レート制限 → 429エラー、待機時間を表示

ユーザーへの表示:
  - 技術用語を使わない
  - 具体的な対処法を提示
  - エラーコードは隠す（開発者コンソールのみ）
```

## 開発フロー

### ブランチ戦略（Git使用時）
```yaml
main: 本番環境
develop: 開発環境（MVP時は不要、mainのみでOK）
feature/*: 機能開発（Phase 11以降）
```

### コミットメッセージ
```yaml
形式:
  - feat: 新機能追加
  - fix: バグ修正
  - docs: ドキュメント更新
  - style: コードフォーマット
  - refactor: リファクタリング
  - test: テスト追加・修正
  - chore: ビルド、設定等

例:
  - feat: add image upload functionality
  - fix: correct API timeout handling
  - docs: update README with setup instructions
```

### デプロイフロー
```yaml
フロントエンド（Vercel）:
  1. GitHubにpush
  2. Vercelが自動デプロイ
  3. プレビューURL確認
  4. 本番反映

バックエンド（Cloud Run）:
  1. Dockerイメージビルド
  2. Google Container Registryにpush
  3. Cloud Runにデプロイ
  4. ヘルスチェック確認
```

---

### 13. E2Eテスト自律実行の絶対原則

**【重要】セッション開始時・compact後の自動判定**

このセクションはE2Eテストオーケストレーターによって自動生成されました。

---

**最初に必ず専門知識を注入してください**

E2Eテスト実行中の場合、以下を実行してから開始してください：

```
inject_knowledge ツールで keyword: "@E2Eテストオーケストレーター"
を実行してから開始してください。（初回必須・compact後も必須）
```

重要：キーワードは "@E2Eテストオーケストレーター"
をそのまま使用してください。変換や推測は不要です。

準備完了です。まず知識注入を実行してから、タスクを開始してください。

---

**E2Eテストオーケストレーター実行中の判定**:
- SCOPE_PROGRESS.mdに「## 📊 E2Eテスト全体進捗」が存在する場合
- または、セッション再開時に前回のメッセージに「E2Eテスト」「オーケストレーター」キーワードがある場合

**セッション開始時・compact後の自動処理**:
1. 上記の判定基準でE2Eテスト実行中と判定
2. inject_knowledge('@E2Eテストオーケストレーター') を必ず実行
3. docs/e2e-best-practices.md の存在確認（なければ初期テンプレート作成）
4. SCOPE_PROGRESS.mdから [ ] テストの続きを自動で特定
5. [x] のテストは絶対にスキップ
6. ユーザー確認不要、完全自律モードで継続
7. ページ選定も自動（未完了ページを上から順に選択）
8. 停止条件：全テスト100%完了のみ

**5回エスカレーション後の処理**:
- チェックリストに [-] マークを付ける
- docs/e2e-test-history/skipped-tests.md に記録
- 次のテストへ自動で進む（停止しない）

**ベストプラクティス自動蓄積**:
- 各テストで成功した方法を docs/e2e-best-practices.md に自動保存
- 後続テストが前のテストの知見を自動活用
- 試行錯誤が減っていく（学習効果）

**重要**:
- この原則はCLAUDE.mdに記載されているため、compact後も自動で適用される
- セッション開始時にこのセクションがない場合、オーケストレーターが自動で追加する

---

**最終更新日**: 2025-11-25
**バージョン**: 1.0（MVP）
