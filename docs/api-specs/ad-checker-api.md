# メタ広告審査チェッカー API仕様書

生成日: 2025-11-22
収集元: frontend/src/services/mock/AdCheckerService.ts
@MOCK_TO_APIマーク数: 1

---

## エンドポイント一覧

### 1. 広告審査AI判定

- **エンドポイント**: `POST /api/check`
- **APIパス定数**: なし（直接指定）
- **Request**: `AdCheckRequest`
- **Response**: `AdCheckResponse`
- **説明**: 広告テキストと画像を総合的にチェックし、メタ広告審査の合否予測と改善提案を返却

#### Request 型定義

```typescript
interface AdCheckRequest {
  headline?: string;        // 見出し（最大255文字）
  description?: string;     // 説明文（最大2000文字）
  cta?: string;            // CTA（最大30文字）
  image?: string;          // 画像（Base64エンコード）
  image_url?: string;      // 画像URL（オプション）
  page_url?: string;       // ランディングページURL（オプション）
}
```

**制約**:
- `headline`, `description`, `cta`, `image` のいずれか1つ以上が必須
- 画像形式: JPEG, PNG, WebP
- 画像サイズ: 最大20MB
- Base64エンコード必須

#### Response 型定義

```typescript
interface AdCheckResponse {
  overall_score: number;              // 総合スコア（0-100）
  status: AdStatus;                   // 'approved' | 'needs_review' | 'rejected'
  confidence: number;                 // 信頼度（0.0-1.0）
  violations: Violation[];            // 違反項目配列
  recommendations: Recommendation[];  // 改善提案配列
  text_overlay_percentage?: number;   // 画像内テキスト量（0-100）
  nsfw_detected: boolean;            // NSFW検出結果
  prohibited_content: string[];      // 禁止コンテンツリスト
  checked_at: string;                // チェック日時（ISO 8601）
  api_used: string;                  // 使用したAI API
}

interface Violation {
  category: ViolationCategory;  // 違反カテゴリ
  severity: 'high' | 'medium' | 'low';  // 重要度
  description: string;          // 具体的な問題点
  location: 'text' | 'image' | 'both';  // 問題箇所
}

type ViolationCategory =
  | 'text_overlay'        // 画像内テキスト量
  | 'prohibited_content'  // 禁止コンテンツ
  | 'nsfw'               // 不適切コンテンツ
  | 'before_after'       // ビフォーアフター表現
  | 'misleading';        // 誇大広告

interface Recommendation {
  before: string;  // 修正前
  after: string;   // 修正後
  reason: string;  // 理由
}
```

#### 処理フロー

1. **リクエストバリデーション**
   - テキストまたは画像が存在するか確認
   - 画像サイズ・形式チェック

2. **画像の前処理（画像がある場合）**
   - Base64エンコード検証
   - サイズ最適化（必要に応じて）

3. **Gemini APIへのリクエスト送信**
   - プロンプト構築（メタ広告審査基準を含む）
   - テキスト + 画像を同時送信
   - タイムアウト: 30秒

4. **AI応答の解析**
   - JSON形式で結果を抽出
   - スコア計算（0-100）
   - ステータス判定（approved/needs_review/rejected）

5. **補助チェック（オプション）**
   - OpenAI Moderation APIで有害コンテンツ検出
   - 結果をマージ

6. **レスポンス整形**
   - 構造化されたJSON形式で返却

#### レスポンス例

**承認（approved）**:
```json
{
  "overall_score": 85,
  "status": "approved",
  "confidence": 0.92,
  "violations": [
    {
      "category": "text_overlay",
      "severity": "medium",
      "description": "画像内のテキスト量が約25%です。Metaは20%以下を推奨しているため、リーチが制限される可能性があります。",
      "location": "image"
    }
  ],
  "recommendations": [
    {
      "before": "業界最安値で高品質なサービスを提供します",
      "after": "お手頃価格で高品質なサービスを提供します",
      "reason": "「最安値」という絶対表現を避けることで、誇大広告リスクを軽減"
    }
  ],
  "text_overlay_percentage": 25,
  "nsfw_detected": false,
  "prohibited_content": [],
  "checked_at": "2025-11-22T12:00:00.000Z",
  "api_used": "gemini-2.5-flash"
}
```

**要審査（needs_review）**:
```json
{
  "overall_score": 65,
  "status": "needs_review",
  "confidence": 0.78,
  "violations": [
    {
      "category": "text_overlay",
      "severity": "high",
      "description": "画像内のテキスト量が約35%です。Metaのガイドラインを大幅に超えているため、審査落ちの可能性が高いです。",
      "location": "image"
    },
    {
      "category": "before_after",
      "severity": "high",
      "description": "ビフォーアフター表現が検出されました。美容・ダイエット分野では禁止されています。",
      "location": "both"
    }
  ],
  "recommendations": [
    {
      "before": "使用前と比べて劇的な変化！100%保証",
      "after": "多くのお客様が満足されています",
      "reason": "ビフォーアフター表現と断定表現を削除し、客観的な表現に変更"
    }
  ],
  "text_overlay_percentage": 35,
  "nsfw_detected": false,
  "prohibited_content": [],
  "checked_at": "2025-11-22T12:00:00.000Z",
  "api_used": "gemini-2.5-flash"
}
```

**却下（rejected）**:
```json
{
  "overall_score": 35,
  "status": "rejected",
  "confidence": 0.95,
  "violations": [
    {
      "category": "prohibited_content",
      "severity": "high",
      "description": "医薬品に関する表現が検出されました。医薬品広告は特別な許可が必要です。",
      "location": "text"
    },
    {
      "category": "nsfw",
      "severity": "high",
      "description": "不適切なコンテンツが検出されました。Metaの広告ポリシーに違反しています。",
      "location": "image"
    }
  ],
  "recommendations": [
    {
      "before": "この薬を飲めば病気が治ります",
      "after": "健康的な生活をサポートする製品です",
      "reason": "医薬品的な効果効能の表現を削除"
    }
  ],
  "text_overlay_percentage": 60,
  "nsfw_detected": true,
  "prohibited_content": ["医薬品", "センシティブコンテンツ"],
  "checked_at": "2025-11-22T12:00:00.000Z",
  "api_used": "gemini-2.5-flash"
}
```

#### エラーハンドリング

| エラーコード | 説明 | 対処法 |
|------------|------|--------|
| 400 | バリデーションエラー（テキスト/画像未入力、サイズ超過等） | 入力内容を確認 |
| 413 | 画像サイズ超過（20MB以上） | 画像を圧縮 |
| 415 | 非対応形式（JPEG/PNG/WebP以外） | 対応形式に変換 |
| 429 | レート制限超過 | 待機してリトライ |
| 500 | サーバーエラー | リトライ（最大3回） |
| 503 | サービス利用不可（タイムアウト） | 時間を置いて再試行 |

#### モックサービス参照

実装時はこのモックサービスの挙動を参考にする:
```
frontend/src/services/mock/AdCheckerService.ts
```

---

## 外部サービス依存

### Google Gemini API
- **モデル**: gemini-2.5-flash
- **用途**: テキスト + 画像の総合審査判定
- **無料枠**: 1分あたり15リクエスト、1日1,500リクエスト
- **タイムアウト**: 30秒
- **リトライ**: 最大3回（指数バックオフ）

### OpenAI Moderation API（オプション）
- **用途**: 有害コンテンツ検出（補助）
- **料金**: 完全無料
- **検出カテゴリ**: 性的、暴力、ヘイト、自傷、違法等

---

## セキュリティ要件

- **認証**: 不要（MVPはパブリックアクセス）
- **レート制限**: MVPでは未実装（将来的にIPベース制限を検討）
- **画像検証**: MIME type検証、サイズ制限、悪意のあるファイル対策
- **API キー管理**: 環境変数で管理（.env.local）

---

## パフォーマンス要件

- **レスポンス時間**: 30秒以内（画像処理含む）
- **スループット**: 無料枠内（月45,000リクエスト）
- **同時接続**: Cloud Runの無料枠制限内

---

**最終更新日**: 2025-11-22
**バージョン**: 1.0（MVP）
