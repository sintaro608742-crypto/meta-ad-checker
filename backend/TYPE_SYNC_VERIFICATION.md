# 型定義同期検証レポート

## 検証日時
2025-11-23

## 対象ファイル
- **フロントエンド**: `frontend/src/types/index.ts`
- **バックエンド**: `backend/src/types.py`

## 検証結果

### ✅ Request Types

#### AdCheckRequest
| フィールド | フロントエンド (TypeScript) | バックエンド (Python) | 同期状態 |
|-----------|---------------------------|---------------------|---------|
| headline | `string?` (optional) | `Optional[str]` (max_length=255) | ✅ |
| description | `string?` (optional) | `Optional[str]` (max_length=2000) | ✅ |
| cta | `string?` (optional) | `Optional[str]` (max_length=30) | ✅ |
| image | `File \| string?` (optional) | `Optional[str]` (Base64) | ✅ |
| image_url | `string?` (optional) | `Optional[str]` | ✅ |
| page_url | `string?` (optional) | `Optional[str]` | ✅ |

**注記**: フロントエンドの`image: File | string`は、バックエンドに送信時にBase64文字列に変換されるため、バックエンドは`str`のみ受け付ける。

---

### ✅ Response Types

#### AdStatus
| フロントエンド | バックエンド | 同期状態 |
|--------------|------------|---------|
| `'approved'` | `APPROVED = "approved"` | ✅ |
| `'needs_review'` | `NEEDS_REVIEW = "needs_review"` | ✅ |
| `'rejected'` | `REJECTED = "rejected"` | ✅ |

#### ViolationSeverity
| フロントエンド | バックエンド | 同期状態 |
|--------------|------------|---------|
| `'high'` | `HIGH = "high"` | ✅ |
| `'medium'` | `MEDIUM = "medium"` | ✅ |
| `'low'` | `LOW = "low"` | ✅ |

#### ViolationCategory
| フロントエンド | バックエンド | 同期状態 |
|--------------|------------|---------|
| `'text_overlay'` | `TEXT_OVERLAY = "text_overlay"` | ✅ |
| `'prohibited_content'` | `PROHIBITED_CONTENT = "prohibited_content"` | ✅ |
| `'nsfw'` | `NSFW = "nsfw"` | ✅ |
| `'before_after'` | `BEFORE_AFTER = "before_after"` | ✅ |
| `'misleading'` | `MISLEADING = "misleading"` | ✅ |

#### Violation
| フィールド | フロントエンド | バックエンド | 同期状態 |
|-----------|--------------|------------|---------|
| category | `ViolationCategory` | `ViolationCategory` | ✅ |
| severity | `ViolationSeverity` | `ViolationSeverity` | ✅ |
| description | `string` | `str` | ✅ |
| location | `'text' \| 'image' \| 'both'` | `ViolationLocation` enum | ✅ |

#### Recommendation
| フィールド | フロントエンド | バックエンド | 同期状態 |
|-----------|--------------|------------|---------|
| before | `string` | `str` | ✅ |
| after | `string` | `str` | ✅ |
| reason | `string` | `str` | ✅ |

#### AdCheckResponse
| フィールド | フロントエンド | バックエンド | 同期状態 |
|-----------|--------------|------------|---------|
| overall_score | `number` (0-100) | `int` (ge=0, le=100) | ✅ |
| status | `AdStatus` | `AdStatus` | ✅ |
| confidence | `number` (0.0-1.0) | `float` (ge=0.0, le=1.0) | ✅ |
| violations | `Violation[]` | `list[Violation]` | ✅ |
| recommendations | `Recommendation[]` | `list[Recommendation]` | ✅ |
| text_overlay_percentage | `number?` (0-100) | `Optional[float]` (ge=0, le=100) | ✅ |
| nsfw_detected | `boolean` | `bool` | ✅ |
| prohibited_content | `string[]` | `list[str]` | ✅ |
| checked_at | `string` (ISO 8601) | `str` (ISO 8601) | ✅ |
| api_used | `string` | `str` | ✅ |

---

### ✅ Error Response Types

#### ApiError
| フィールド | フロントエンド | バックエンド | 同期状態 |
|-----------|--------------|------------|---------|
| error | `string` | `str` | ✅ |
| message | `string` | `str` | ✅ |
| details | `Record<string, unknown>?` | `Optional[dict]` | ✅ |

---

### ✅ Health Check Types

#### HealthCheckResponse
| フィールド | フロントエンド | バックエンド | 同期状態 |
|-----------|--------------|------------|---------|
| status | `'healthy' \| 'unhealthy'` | `HealthStatus` enum | ✅ |
| timestamp | `string` (ISO 8601) | `str` (ISO 8601) | ✅ |

---

## 総括

### 🎉 完全同期達成

全ての型定義がフロントエンドとバックエンドで完全に同期しています。

### バリデーション強化点（バックエンド）

バックエンドでは以下の追加バリデーションを実装:

1. **文字数制限**
   - `headline`: 最大255文字
   - `description`: 最大2000文字
   - `cta`: 最大30文字

2. **数値範囲バリデーション**
   - `overall_score`: 0-100
   - `confidence`: 0.0-1.0
   - `text_overlay_percentage`: 0-100

3. **空文字列の正規化**
   - 空白のみの文字列は`None`に変換

4. **コンテンツ存在チェック**
   - `AdCheckRequest.has_content()`メソッドで少なくとも1つのフィールドが入力されているか検証

### ヘルパーメソッド

#### AdCheckResponse
- `create_with_timestamp()`: タイムスタンプを自動生成

#### HealthCheckResponse
- `create_healthy()`: 正常なレスポンスを生成
- `create_unhealthy()`: 異常なレスポンスを生成

---

## 今後の運用ルール

1. **変更時の同期手順**
   - フロントエンド型定義を変更した場合、必ずバックエンド型定義も同時に更新
   - このドキュメントも更新して検証記録を残す

2. **型定義の追加**
   - 新しい型を追加する場合、両方のファイルに同時に追加
   - API仕様書 (`docs/api-specs/ad-checker-api.md`) も更新

3. **破壊的変更の禁止**
   - MVPフェーズでは既存フィールドの削除や型変更は禁止
   - 拡張のみ許可（新規フィールド追加はオプションで）

---

**検証者**: Claude Code
**バージョン**: 1.0（MVP）
