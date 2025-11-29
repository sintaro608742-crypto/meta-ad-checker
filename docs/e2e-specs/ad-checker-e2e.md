# AdChecker E2Eテスト仕様書

## 概要

本ドキュメントは、メタ広告審査チェッカーのメインページ（AdCheckerPage）のE2Eテスト仕様を定義します。

- **対象ページ**: `/`
- **実装ファイル**: `frontend/src/pages/AdCheckerPage.tsx`
- **モックサービス**: `frontend/src/services/mock/AdCheckerService.ts`
- **テストフレームワーク**: Playwright（推奨）
- **作成日**: 2025-11-22
- **最終更新日**: 2025-11-22

---

## テスト環境

### 前提条件

```yaml
フロントエンド:
  URL: http://localhost:3247
  ポート: 3247

バックエンド:
  URL: http://localhost:8432
  ポート: 8432
  モード: モックサービス使用（API未実装時）

ブラウザ:
  - Chrome (最新版)
  - Firefox (最新版)
  - Safari (最新版)
  - Mobile Safari (iOS)
  - Chrome Mobile (Android)

画面サイズ:
  - Desktop: 1920x1080
  - Tablet: 768x1024
  - Mobile: 375x667
```

### テストデータ

```yaml
画像ファイル:
  有効なファイル:
    - test-image-valid.jpg (1MB, JPEG)
    - test-image-valid.png (2MB, PNG)
    - test-image-valid.webp (500KB, WebP)
    - test-image-max.jpg (19.5MB, JPEG - 最大サイズ近く)

  無効なファイル:
    - test-image-too-large.jpg (21MB - サイズ超過)
    - test-document.pdf (1MB - 非対応形式)
    - test-image.gif (1MB - 非対応形式)
    - test-image.svg (100KB - 非対応形式)

テキスト入力:
  承認パターン:
    - headline: "今すぐダウンロード"
    - description: "お手頃価格で高品質なサービスを提供します"
    - cta: "詳細を見る"

  要審査パターン:
    - headline: "最安値で提供"
    - description: "100%満足保証"
    - cta: "今すぐ購入"

  却下パターン:
    - headline: "病気が治る薬"
    - description: "この薬を飲めば病気が治ります"
    - cta: "大幅セール"
```

---

## テストケース一覧

### カテゴリ分類

1. **正常系テスト** (TC-001 ~ TC-015): 基本機能の正常動作
2. **異常系テスト** (TC-101 ~ TC-115): エラーハンドリング
3. **バリデーションテスト** (TC-201 ~ TC-210): 入力検証
4. **セキュリティテスト** (TC-301 ~ TC-305): セキュリティ脆弱性
5. **レスポンシブテスト** (TC-401 ~ TC-410): 画面サイズ対応
6. **パフォーマンステスト** (TC-501 ~ TC-505): 速度・負荷

---

## 1. 正常系テスト

### TC-001: ページ初期表示

**優先度**: Critical
**実行頻度**: 毎回

**テスト手順**:
1. ブラウザで `http://localhost:3247/` にアクセス

**期待結果**:
- ページタイトル「メタ広告審査チェッカー」が表示される
- 3つの入力フィールド（見出し、説明文、CTA）が表示される
- 画像アップロードエリアが表示される
- 「AIチェック実行」ボタンが無効状態（グレーアウト）
- 結果表示エリアが非表示
- エラーメッセージが非表示
- グラデーション背景が正しく表示される

**検証ポイント**:
```typescript
await expect(page.locator('h1')).toContainText('メタ広告審査チェッカー');
await expect(page.locator('input[label="見出し（任意）"]')).toBeVisible();
await expect(page.locator('textarea[label="説明文（任意）"]')).toBeVisible();
await expect(page.locator('input[label="CTA（任意）"]')).toBeVisible();
await expect(page.locator('text=画像をドラッグ&ドロップ')).toBeVisible();
await expect(page.locator('button:has-text("AIチェック実行")')).toBeDisabled();
```

---

### TC-002: テキストのみで広告チェック実行（承認パターン）

**優先度**: Critical
**実行頻度**: 毎回

**テスト手順**:
1. 見出しに「今すぐダウンロード」と入力
2. 説明文に「お手頃価格で高品質なサービスを提供します」と入力
3. CTAに「詳細を見る」と入力
4. 「AIチェック実行」ボタンをクリック
5. ローディング表示を確認
6. 2秒待機（モック処理時間）
7. 結果表示を確認

**期待結果**:
- ボタンが活性化される
- クリック後、ボタンが「審査チェック中...」に変わる
- CircularProgressが表示される
- 約2秒後、結果が表示される
- 総合スコア: 85%
- ステータスバッジ: 「承認される可能性が高い」（緑色）
- 問題箇所: 2件表示
  - 画像内テキスト量（中）
  - 誇大広告表現（低）
- 改善提案: 1件表示
- 詳細情報: 信頼度92%、NSFW検出なし

**検証ポイント**:
```typescript
// 入力後、ボタン活性化
await expect(page.locator('button:has-text("AIチェック実行")')).toBeEnabled();

// ローディング状態
await page.click('button:has-text("AIチェック実行")');
await expect(page.locator('button:has-text("審査チェック中...")')).toBeVisible();

// 結果表示（2秒後）
await page.waitForSelector('text=85%', { timeout: 5000 });
await expect(page.locator('text=総合審査スコア')).toBeVisible();
await expect(page.locator('text=承認される可能性が高い')).toBeVisible();
await expect(page.locator('text=問題箇所の指摘')).toBeVisible();
await expect(page.locator('text=改善提案（コピペで使えます）')).toBeVisible();
```

---

### TC-003: テキストのみで広告チェック実行（要審査パターン）

**優先度**: High
**実行頻度**: 毎回

**テスト手順**:
1. 見出しに「最安値で提供」と入力
2. 説明文に「100%満足保証」と入力
3. CTAに「今すぐ購入」と入力
4. 「AIチェック実行」ボタンをクリック
5. 結果表示を確認

**期待結果**:
- 総合スコア: 65%
- ステータスバッジ: 「要審査」（オレンジ色）
- 問題箇所: 3件表示
  - 画像内テキスト量（高）
  - ビフォーアフター表現（高）
  - 誇大広告表現（中）
- 改善提案: 2件表示
- 詳細情報: 信頼度78%、NSFW検出なし

---

### TC-004: テキストのみで広告チェック実行（却下パターン）

**優先度**: High
**実行頻度**: 毎回

**テスト手順**:
1. 見出しに「病気が治る薬」と入力
2. 説明文に「この薬を飲めば病気が治ります」と入力
3. CTAに「大幅セール」と入力
4. 「AIチェック実行」ボタンをクリック
5. 結果表示を確認

**期待結果**:
- 総合スコア: 35%
- ステータスバッジ: 「却下される可能性が高い」（赤色）
- 問題箇所: 3件表示
  - 禁止コンテンツ（高）
  - 不適切なコンテンツ（高）
  - 画像内テキスト量（高）
- 改善提案: 2件表示
- 詳細情報: 信頼度95%、NSFW検出あり

---

### TC-005: 画像のみで広告チェック実行

**優先度**: High
**実行頻度**: 毎回

**テスト手順**:
1. テキストフィールドは全て空欄のまま
2. 画像アップロードエリアをクリック
3. ファイル選択ダイアログから `test-image-valid.jpg` を選択
4. 画像プレビューが表示されることを確認
5. 「AIチェック実行」ボタンをクリック
6. 結果表示を確認

**期待結果**:
- 画像プレビューが表示される
- プレビュー右上に削除ボタン（ゴミ箱アイコン）が表示される
- ボタンが活性化される
- チェック実行後、結果が表示される
- テキスト関連の違反は表示されない（画像のみ）

**検証ポイント**:
```typescript
// ファイル選択
await page.setInputFiles('input[type="file"]', 'test-image-valid.jpg');

// プレビュー表示
await expect(page.locator('img[alt="プレビュー"]')).toBeVisible();
await expect(page.locator('button:has(svg[data-testid="DeleteIcon"])')).toBeVisible();

// ボタン活性化
await expect(page.locator('button:has-text("AIチェック実行")')).toBeEnabled();
```

---

### TC-006: テキスト + 画像で広告チェック実行

**優先度**: Critical
**実行頻度**: 毎回

**テスト手順**:
1. 見出しに「今すぐダウンロード」と入力
2. 説明文に「お手頃価格で高品質なサービスを提供します」と入力
3. CTAに「詳細を見る」と入力
4. 画像ファイル `test-image-valid.png` をアップロード
5. 「AIチェック実行」ボタンをクリック
6. 結果表示を確認

**期待結果**:
- 総合スコア、ステータス、違反、改善提案が表示される
- 画像内テキスト量（%）が表示される
- 信頼度、NSFW検出が表示される

---

### TC-007: ドラッグ&ドロップで画像アップロード

**優先度**: High
**実行頻度**: 定期

**テスト手順**:
1. ファイルマネージャーから `test-image-valid.webp` をドラッグ
2. 画像アップロードエリア上でホバー
3. ドロップエリアの色が変わることを確認
4. ファイルをドロップ
5. 画像プレビューが表示されることを確認

**期待結果**:
- ドラッグ中、エリアの背景色が変わる（`#d1fae5`）
- ボーダー色が変わる（`primary.main`）
- ドロップ後、画像プレビューが表示される
- ボタンが活性化される

**検証ポイント**:
```typescript
// ドラッグ中の状態変化を確認
const dropzone = page.locator('[data-testid="dropzone"]');
await dropzone.dragOver({ file: 'test-image-valid.webp' });
await expect(dropzone).toHaveCSS('background', /linear-gradient.*#d1fae5/);

// ドロップ後
await dropzone.drop({ file: 'test-image-valid.webp' });
await expect(page.locator('img[alt="プレビュー"]')).toBeVisible();
```

---

### TC-008: 画像プレビューの削除

**優先度**: High
**実行頻度**: 定期

**テスト手順**:
1. 画像ファイル `test-image-valid.jpg` をアップロード
2. 画像プレビューが表示されることを確認
3. プレビュー右上の削除ボタン（ゴミ箱アイコン）をクリック
4. プレビューが消えることを確認

**期待結果**:
- 削除ボタンクリック後、プレビューが非表示になる
- 画像データがクリアされる
- ボタンが無効化される（他の入力がない場合）

**検証ポイント**:
```typescript
// 削除前
await expect(page.locator('img[alt="プレビュー"]')).toBeVisible();

// 削除実行
await page.click('button:has(svg[data-testid="DeleteIcon"])');

// 削除後
await expect(page.locator('img[alt="プレビュー"]')).not.toBeVisible();
await expect(page.locator('button:has-text("AIチェック実行")')).toBeDisabled();
```

---

### TC-009: 再チェック機能

**優先度**: High
**実行頻度**: 定期

**テスト手順**:
1. TC-002の手順で広告チェックを実行
2. 結果が表示されることを確認
3. 「修正内容を再チェック」ボタンをクリック
4. 結果表示エリアが消えることを確認
5. 入力内容とプレビュー画像が保持されることを確認
6. 「AIチェック実行」ボタンが活性化されていることを確認

**期待結果**:
- 再チェックボタンクリック後、結果エリアが非表示になる
- テキスト入力内容は保持される
- 画像プレビューは保持される
- すぐに再実行可能な状態になる

**検証ポイント**:
```typescript
// 結果表示後
await expect(page.locator('text=総合審査スコア')).toBeVisible();

// 再チェックボタンクリック
await page.click('button:has-text("修正内容を再チェック")');

// 結果非表示、入力保持
await expect(page.locator('text=総合審査スコア')).not.toBeVisible();
await expect(page.locator('input[label="見出し（任意）"]')).toHaveValue('今すぐダウンロード');
await expect(page.locator('img[alt="プレビュー"]')).toBeVisible();
```

---

### TC-010: 最大文字数入力（見出し）

**優先度**: Medium
**実行頻度**: 定期

**テスト手順**:
1. 見出しフィールドに255文字の文字列を入力
2. 256文字目を入力しようとする
3. 入力が制限されることを確認

**期待結果**:
- 255文字まで入力可能
- 256文字目は入力できない
- 入力中にエラーメッセージは表示されない

**検証ポイント**:
```typescript
const maxLengthText = 'a'.repeat(255);
await page.fill('input[label="見出し（任意）"]', maxLengthText);
await expect(page.locator('input[label="見出し（任意）"]')).toHaveValue(maxLengthText);

// 256文字目を入力
await page.type('input[label="見出し（任意）"]', 'x');
await expect(page.locator('input[label="見出し（任意）"]')).toHaveValue(maxLengthText);
```

---

### TC-011: 最大文字数入力（説明文）

**優先度**: Medium
**実行頻度**: 定期

**テスト手順**:
1. 説明文フィールドに2000文字の文字列を入力
2. 2001文字目を入力しようとする
3. 入力が制限されることを確認

**期待結果**:
- 2000文字まで入力可能
- 2001文字目は入力できない

---

### TC-012: 最大文字数入力（CTA）

**優先度**: Medium
**実行頻度**: 定期

**テスト手順**:
1. CTAフィールドに30文字の文字列を入力
2. 31文字目を入力しようとする
3. 入力が制限されることを確認

**期待結果**:
- 30文字まで入力可能
- 31文字目は入力できない

---

### TC-013: 複数ファイル選択時の挙動

**優先度**: Low
**実行頻度**: 定期

**テスト手順**:
1. ファイル選択ダイアログで複数のファイルを選択
2. 最初の1ファイルのみがアップロードされることを確認

**期待結果**:
- 複数ファイル選択しても、最初の1ファイルのみ処理される
- エラーは発生しない

---

### TC-014: 画像の再アップロード（上書き）

**優先度**: Medium
**実行頻度**: 定期

**テスト手順**:
1. 画像ファイル `test-image-valid.jpg` をアップロード
2. プレビューが表示されることを確認
3. 別の画像ファイル `test-image-valid.png` をアップロード
4. プレビューが新しい画像に置き換わることを確認

**期待結果**:
- 新しい画像がプレビューに表示される
- 古いプレビューURLは解放される（メモリリーク防止）

---

### TC-015: 各セクションのホバー効果

**優先度**: Low
**実行頻度**: 手動

**テスト手順**:
1. 「広告テキスト」Paperにマウスホバー
2. 「広告画像」Paperにマウスホバー
3. 「チェック実行ボタン」Paperにマウスホバー
4. アニメーション効果を確認

**期待結果**:
- ホバー時、Paperが上に移動（`translateY(-2px)`）
- ボックスシャドウが濃くなる
- スムーズな遷移アニメーション（0.3s）

---

## 2. 異常系テスト

### TC-101: 入力なしでチェック実行

**優先度**: Critical
**実行頻度**: 毎回

**テスト手順**:
1. すべてのフィールドを空欄のまま
2. 「AIチェック実行」ボタンの状態を確認

**期待結果**:
- ボタンが無効化されている（クリック不可）
- グレーアウト表示
- 注意文「※テキストまたは画像の少なくとも1つが必要です」が表示される

**検証ポイント**:
```typescript
await expect(page.locator('button:has-text("AIチェック実行")')).toBeDisabled();
await expect(page.locator('text=テキストまたは画像の少なくとも1つが必要です')).toBeVisible();
```

---

### TC-102: ファイルサイズ超過（21MB）

**優先度**: Critical
**実行頻度**: 毎回

**テスト手順**:
1. 21MBの画像ファイル `test-image-too-large.jpg` をアップロード
2. エラーメッセージが表示されることを確認

**期待結果**:
- ファイル選択直後、エラーメッセージが表示される
- エラーメッセージ: 「ファイルサイズは20MB以下にしてください」
- 画像プレビューは表示されない
- ボタンは無効化されたまま

**検証ポイント**:
```typescript
await page.setInputFiles('input[type="file"]', 'test-image-too-large.jpg');
await expect(page.locator('text=ファイルサイズは20MB以下にしてください')).toBeVisible();
await expect(page.locator('img[alt="プレビュー"]')).not.toBeVisible();
```

---

### TC-103: 非対応ファイル形式（PDF）

**優先度**: High
**実行頻度**: 毎回

**テスト手順**:
1. PDFファイル `test-document.pdf` をアップロード
2. エラーメッセージが表示されることを確認

**期待結果**:
- エラーメッセージ: 「対応形式: JPEG, PNG, WebPのみアップロード可能です」
- 画像プレビューは表示されない

---

### TC-104: 非対応ファイル形式（GIF）

**優先度**: Medium
**実行頻度**: 定期

**テスト手順**:
1. GIFファイル `test-image.gif` をアップロード
2. エラーメッセージが表示されることを確認

**期待結果**:
- エラーメッセージ: 「対応形式: JPEG, PNG, WebPのみアップロード可能です」

---

### TC-105: 非対応ファイル形式（SVG）

**優先度**: Medium
**実行頻度**: 定期

**テスト手順**:
1. SVGファイル `test-image.svg` をアップロード
2. エラーメッセージが表示されることを確認

**期待結果**:
- エラーメッセージ: 「対応形式: JPEG, PNG, WebPのみアップロード可能です」

---

### TC-106: ネットワークエラー時の挙動

**優先度**: High
**実行頻度**: 定期

**テスト手順**:
1. ネットワークをオフラインに設定
2. 広告チェックを実行
3. エラーメッセージが表示されることを確認

**期待結果**:
- ローディング表示が終了する
- エラーメッセージが表示される
- ボタンが再度活性化される（再試行可能）
- 結果は表示されない

**検証ポイント**:
```typescript
// ネットワークをオフライン
await page.context().setOffline(true);

// チェック実行
await page.click('button:has-text("AIチェック実行")');

// エラー表示
await expect(page.locator('[role="alert"]')).toBeVisible();
await expect(page.locator('button:has-text("AIチェック実行")')).toBeEnabled();
```

---

### TC-107: APIタイムアウト（30秒超過）

**優先度**: Medium
**実行頻度**: 定期

**テスト手順**:
1. モックサービスを30秒以上待機するように変更
2. 広告チェックを実行
3. タイムアウトエラーが表示されることを確認

**期待結果**:
- 30秒後、タイムアウトエラーメッセージが表示される
- エラーメッセージに再試行を促す内容が含まれる

---

### TC-108: 連続クリック防止

**優先度**: Medium
**実行頻度**: 定期

**テスト手順**:
1. 広告チェック実行ボタンをクリック
2. ローディング中に再度ボタンをクリック
3. 重複実行されないことを確認

**期待結果**:
- ローディング中、ボタンは無効化される
- 連続クリックしても1回のみ実行される

---

### TC-109: 破損した画像ファイル

**優先度**: Low
**実行頻度**: 手動

**テスト手順**:
1. 拡張子を偽装した破損ファイルをアップロード
2. エラーハンドリングを確認

**期待結果**:
- エラーメッセージが表示される
- プレビュー表示に失敗してもクラッシュしない

---

### TC-110: 空白文字のみの入力

**優先度**: Medium
**実行頻度**: 定期

**テスト手順**:
1. 見出しに「   」（スペースのみ）を入力
2. 説明文に改行のみを入力
3. CTAにタブのみを入力
4. ボタンの状態を確認

**期待結果**:
- ボタンが無効化される（空白文字は入力とみなさない）
- または、API側で空白をトリムして処理

**実装次第**:
```typescript
// フロントエンド側でトリムする場合
const hasInput = !!(
  formData.headline.trim() ||
  formData.description.trim() ||
  formData.cta.trim() ||
  formData.imageFile
);
```

---

### TC-111: 特殊文字入力

**優先度**: Low
**実行頻度**: 手動

**テスト手順**:
1. 見出しに絵文字、記号を含む文字列を入力
   例: "🎉今すぐ<script>alert('test')</script>ダウンロード"
2. 広告チェックを実行
3. 正しく処理されることを確認

**期待結果**:
- HTMLエスケープされて表示される
- XSS攻撃が成立しない
- AIチェックが正常に実行される

---

### TC-112: 同じ画像を削除→再アップロード

**優先度**: Low
**実行頻度**: 定期

**テスト手順**:
1. 画像ファイルをアップロード
2. 削除ボタンで削除
3. 同じ画像ファイルを再度アップロード
4. 正常にアップロードされることを確認

**期待結果**:
- 削除後、同じファイルを再度選択可能
- プレビューが正しく表示される

---

### TC-113: ブラウザバックボタン押下

**優先度**: Medium
**実行頻度**: 定期

**テスト手順**:
1. 広告チェックを実行し、結果を表示
2. ブラウザのバックボタンを押下
3. 動作を確認

**期待結果**:
- SPAのため、ページ遷移は発生しない
- または、ガイドページから戻る場合は正常に戻る

---

### TC-114: ブラウザリロード

**優先度**: Medium
**実行頻度**: 定期

**テスト手順**:
1. テキスト入力、画像アップロード後
2. ブラウザをリロード（F5）
3. 入力内容が消えることを確認

**期待結果**:
- すべての入力内容がクリアされる
- 初期状態に戻る
- エラーは発生しない

---

### TC-115: タブ切り替え後の動作

**優先度**: Low
**実行頻度**: 手動

**テスト手順**:
1. 画像プレビューを表示
2. 別のタブに移動
3. 10分後、元のタブに戻る
4. プレビューが正しく表示されることを確認

**期待結果**:
- プレビューURLが有効（revokeされていない）
- 再チェック実行可能

---

## 3. バリデーションテスト

### TC-201: 見出しフィールドの文字数カウント

**優先度**: Low
**実行頻度**: 手動

**テスト手順**:
1. 見出しフィールドに文字を入力
2. 文字数カウンターが表示される場合、正しくカウントされることを確認

**期待結果**:
- リアルタイムで文字数が更新される
- 最大255文字まで入力可能

**注記**: 現在の実装では文字数カウンターはないが、将来追加する場合のテスト項目

---

### TC-202: 説明文フィールドの文字数カウント

**優先度**: Low
**実行頻度**: 手動

**期待結果**:
- 最大2000文字まで入力可能

---

### TC-203: CTAフィールドの文字数カウント

**優先度**: Low
**実行頻度**: 手動

**期待結果**:
- 最大30文字まで入力可能

---

### TC-204: ファイルサイズの境界値テスト（19.9MB）

**優先度**: Medium
**実行頻度**: 定期

**テスト手順**:
1. 19.9MBの画像ファイルをアップロード
2. 正常にアップロードされることを確認

**期待結果**:
- 20MB以下なので正常にアップロード
- エラーは発生しない

---

### TC-205: ファイルサイズの境界値テスト（20.0MB）

**優先度**: Medium
**実行頻度**: 定期

**テスト手順**:
1. ちょうど20.0MBの画像ファイルをアップロード
2. 正常にアップロードされることを確認

**期待結果**:
- 20MB以下なので正常にアップロード

---

### TC-206: ファイルサイズの境界値テスト（20.1MB）

**優先度**: Medium
**実行頻度**: 定期

**テスト手順**:
1. 20.1MBの画像ファイルをアップロード
2. エラーメッセージが表示されることを確認

**期待結果**:
- エラーメッセージ: 「ファイルサイズは20MB以下にしてください」

---

### TC-207: MIME type検証

**優先度**: Medium
**実行頻度**: 定期

**テスト手順**:
1. 拡張子を `.jpg` に変更したPDFファイルをアップロード
2. MIME type検証でエラーになることを確認

**期待結果**:
- ファイル拡張子ではなくMIME typeで判定
- エラーメッセージが表示される

---

### TC-208: 日本語ファイル名

**優先度**: Low
**実行頻度**: 手動

**テスト手順**:
1. ファイル名が日本語の画像（例: `広告画像.jpg`）をアップロード
2. 正常に処理されることを確認

**期待結果**:
- 日本語ファイル名でも正常にアップロード
- プレビュー表示される

---

### TC-209: 長いファイル名

**優先度**: Low
**実行頻度**: 手動

**テスト手順**:
1. 255文字のファイル名を持つ画像をアップロード
2. 正常に処理されることを確認

**期待結果**:
- 長いファイル名でも正常にアップロード

---

### TC-210: パス区切り文字を含むファイル名

**優先度**: Low
**実行頻度**: 手動

**テスト手順**:
1. ファイル名に `/` や `\` を含むファイル（OS許可する範囲）をアップロード
2. 正常に処理されることを確認

**期待結果**:
- エスケープ処理されて正常にアップロード

---

## 4. セキュリティテスト

### TC-301: XSS攻撃（スクリプトタグ）

**優先度**: Critical
**実行頻度**: 毎回

**テスト手順**:
1. 見出しに `<script>alert('XSS')</script>` と入力
2. 広告チェックを実行
3. 結果表示でスクリプトが実行されないことを確認

**期待結果**:
- スクリプトは実行されず、文字列として表示される
- アラートが表示されない
- HTMLエスケープされている

**検証ポイント**:
```typescript
await page.fill('input[label="見出し（任意）"]', '<script>alert("XSS")</script>');
await page.click('button:has-text("AIチェック実行")');

// 結果表示でエスケープされていることを確認
await expect(page.locator('text=<script>')).toBeVisible(); // テキストとして表示
```

---

### TC-302: XSS攻撃（イベントハンドラ）

**優先度**: Critical
**実行頻度**: 毎回

**テスト手順**:
1. 見出しに `<img src=x onerror=alert('XSS')>` と入力
2. 広告チェックを実行
3. スクリプトが実行されないことを確認

**期待結果**:
- イベントハンドラは実行されない
- HTMLエスケープされている

---

### TC-303: SQLインジェクション（将来のDB対応）

**優先度**: Low
**実行頻度**: 手動

**テスト手順**:
1. 見出しに `'; DROP TABLE users; --` と入力
2. 広告チェックを実行
3. 正常に処理されることを確認

**期待結果**:
- SQLインジェクションは成立しない
- 文字列として扱われる

**注記**: MVP時はDBなしだが、Phase 11拡張時に必須

---

### TC-304: ファイルアップロード脆弱性（悪意のあるJPEG）

**優先度**: High
**実行頻度**: 定期

**テスト手順**:
1. 埋め込みスクリプトを含むJPEGファイルをアップロード
2. サーバー側でスクリプトが実行されないことを確認

**期待結果**:
- ファイルは画像として処理される
- サーバー側で悪意のあるコードは実行されない

---

### TC-305: CSRF攻撃（将来の認証実装時）

**優先度**: Low
**実行頻度**: 手動

**テスト手順**:
1. 外部サイトから広告チェックAPIを呼び出す
2. CSRFトークン検証でエラーになることを確認

**期待結果**:
- CSRFトークンがないリクエストは拒否される

**注記**: MVP時は認証なしだが、Phase 11拡張時に必須

---

## 5. レスポンシブテスト

### TC-401: デスクトップ表示（1920x1080）

**優先度**: High
**実行頻度**: 毎回

**テスト手順**:
1. ビューポートを1920x1080に設定
2. ページを表示
3. レイアウトを確認

**期待結果**:
- タイトルが大きく表示される（3.5rem）
- すべての要素が横並びで適切に配置される
- 詳細情報が3カラムグリッドで表示される
- 余白が適切

**検証ポイント**:
```typescript
await page.setViewportSize({ width: 1920, height: 1080 });
await expect(page.locator('h1')).toHaveCSS('font-size', '56px'); // 3.5rem
await expect(page.locator('[data-testid="detail-grid"]')).toHaveCSS('grid-template-columns', 'repeat(3, 1fr)');
```

---

### TC-402: タブレット表示（768x1024）

**優先度**: High
**実行頻度**: 毎回

**テスト手順**:
1. ビューポートを768x1024に設定
2. ページを表示
3. レイアウトを確認

**期待結果**:
- タイトルサイズが調整される
- 詳細情報が3カラムまたは2カラムで表示される
- 横スクロールが発生しない

---

### TC-403: モバイル表示（375x667）

**優先度**: Critical
**実行頻度**: 毎回

**テスト手順**:
1. ビューポートを375x667に設定（iPhone SE）
2. ページを表示
3. レイアウトを確認

**期待結果**:
- タイトルが小さく表示される（2.5rem）
- すべての要素が縦並びで表示される
- 詳細情報が1カラムで表示される
- テキストフィールドが画面幅に収まる
- ボタンが押しやすいサイズ
- 横スクロールが発生しない

**検証ポイント**:
```typescript
await page.setViewportSize({ width: 375, height: 667 });
await expect(page.locator('h1')).toHaveCSS('font-size', '40px'); // 2.5rem
await expect(page.locator('[data-testid="detail-grid"]')).toHaveCSS('grid-template-columns', '1fr');
```

---

### TC-404: 極小画面（320x568）

**優先度**: Medium
**実行頻度**: 定期

**テスト手順**:
1. ビューポートを320x568に設定（iPhone 5/SE 1st gen）
2. ページを表示
3. レイアウトを確認

**期待結果**:
- すべての要素が表示される
- テキストが読める
- ボタンがタップ可能
- 横スクロールが発生しない

---

### TC-405: 極大画面（2560x1440）

**優先度**: Low
**実行頻度**: 手動

**テスト手順**:
1. ビューポートを2560x1440に設定
2. ページを表示
3. レイアウトを確認

**期待結果**:
- 要素が過度に拡大されない
- 最大幅制限が機能している（`maxWidth="lg"`）
- 中央配置される

---

### TC-406: 横向きモバイル（667x375）

**優先度**: Medium
**実行頻度**: 定期

**テスト手順**:
1. ビューポートを667x375に設定（横向き）
2. ページを表示
3. レイアウトを確認

**期待結果**:
- 横向きでも適切にレイアウトされる
- スクロールで全要素にアクセス可能

---

### TC-407: ピンチズーム

**優先度**: Low
**実行頻度**: 手動

**テスト手順**:
1. モバイルデバイスでピンチズームを実行
2. ズームイン・ズームアウトを確認

**期待結果**:
- ピンチズームが機能する
- ズーム後もレイアウトが崩れない

---

### TC-408: 画像プレビューのレスポンシブ

**優先度**: Medium
**実行頻度**: 定期

**テスト手順**:
1. 各画面サイズで画像をアップロード
2. プレビュー表示を確認

**期待結果**:
- デスクトップ: 最大400px幅
- モバイル: 画面幅に収まる
- アスペクト比が保たれる

---

### TC-409: 長いテキストの表示

**優先度**: Medium
**実行頻度**: 定期

**テスト手順**:
1. モバイル画面で、最大文字数のテキストを入力
2. 表示を確認

**期待結果**:
- テキストが折り返される
- 横スクロールが発生しない
- 読みやすい

---

### TC-410: タッチターゲットサイズ

**優先度**: High
**実行頻度**: 定期

**テスト手順**:
1. モバイル画面でボタン、アイコンのサイズを確認
2. タップ可能性を検証

**期待結果**:
- すべてのタッチターゲットが最低44x44px
- 削除ボタンなどの小さいアイコンも十分なサイズ
- 隣接要素と十分な間隔

**検証ポイント**:
```typescript
const deleteButton = page.locator('button:has(svg[data-testid="DeleteIcon"])');
const bbox = await deleteButton.boundingBox();
expect(bbox?.width).toBeGreaterThanOrEqual(44);
expect(bbox?.height).toBeGreaterThanOrEqual(44);
```

---

## 6. パフォーマンステスト

### TC-501: ページ初期表示速度

**優先度**: High
**実行頻度**: 定期

**テスト手順**:
1. Performance APIを使用してページロード時間を測定
2. LCP、FID、CLSを確認

**期待結果**:
- LCP（Largest Contentful Paint）: 2.5秒以内
- FID（First Input Delay）: 100ms以内
- CLS（Cumulative Layout Shift）: 0.1以内

**検証ポイント**:
```typescript
const performanceTiming = await page.evaluate(() => performance.timing);
const loadTime = performanceTiming.loadEventEnd - performanceTiming.navigationStart;
expect(loadTime).toBeLessThan(2500);
```

---

### TC-502: 画像プレビュー生成速度

**優先度**: Medium
**実行頻度**: 定期

**テスト手順**:
1. 10MBの画像をアップロード
2. プレビュー表示までの時間を測定

**期待結果**:
- 1秒以内にプレビュー表示

---

### TC-503: API呼び出しのレスポンス時間

**優先度**: High
**実行頻度**: 定期

**テスト手順**:
1. 広告チェックを実行
2. API呼び出しからレスポンス受信までの時間を測定

**期待結果**:
- モック環境: 2秒程度（意図的な遅延）
- 本番環境: 5秒以内

---

### TC-504: メモリリーク検証

**優先度**: Medium
**実行頻度**: 定期

**テスト手順**:
1. 画像アップロード→削除を10回繰り返す
2. メモリ使用量を確認

**期待結果**:
- メモリ使用量が増加し続けない
- `URL.revokeObjectURL()` が正しく呼ばれている

**検証ポイント**:
```typescript
// Chrome DevTools Protocol
const session = await page.context().newCDPSession(page);
await session.send('HeapProfiler.enable');

// 10回繰り返し
for (let i = 0; i < 10; i++) {
  await page.setInputFiles('input[type="file"]', 'test-image-valid.jpg');
  await page.click('button:has(svg[data-testid="DeleteIcon"])');
}

// ヒープスナップショット取得
const snapshot = await session.send('HeapProfiler.takeHeapSnapshot');
// メモリ使用量が異常に増加していないことを確認
```

---

### TC-505: 連続リクエスト時の動作

**優先度**: Low
**実行頻度**: 手動

**テスト手順**:
1. 広告チェックを5回連続で実行
2. 各リクエストが正常に処理されることを確認

**期待結果**:
- すべてのリクエストが成功
- レート制限にかからない（MVP時）
- UIが正常に動作

---

## テスト実行計画

### 優先度別実行頻度

```yaml
Critical（最重要）:
  - 実行頻度: 毎回のCI/CD実行時
  - テストケース: TC-001, TC-002, TC-101, TC-102, TC-103, TC-301, TC-302, TC-403

High（重要）:
  - 実行頻度: プルリクエスト時
  - テストケース: TC-003, TC-004, TC-005, TC-006, TC-007, TC-008, TC-009, TC-106, TC-304, TC-401, TC-402, TC-410, TC-501, TC-503

Medium（中）:
  - 実行頻度: 週次実行
  - テストケース: TC-010, TC-011, TC-012, TC-014, TC-107, TC-108, TC-110, TC-113, TC-114, TC-204, TC-205, TC-206, TC-207, TC-404, TC-406, TC-408, TC-409, TC-502, TC-504

Low（低）:
  - 実行頻度: リリース前実行
  - テストケース: その他すべて
```

### CI/CDパイプライン統合

```yaml
GitHub Actions設定例:
  テストステップ:
    - name: E2E Tests (Critical)
      run: npx playwright test --grep "@critical"

    - name: E2E Tests (High)
      run: npx playwright test --grep "@high"
      if: github.event_name == 'pull_request'

    - name: E2E Tests (All)
      run: npx playwright test
      if: github.ref == 'refs/heads/main'
```

---

## テストデータ管理

### テスト画像の準備

```bash
# テスト画像生成スクリプト（ImageMagick使用）

# 有効なJPEG（1MB）
convert -size 1000x1000 xc:white test-image-valid.jpg

# 有効なPNG（2MB）
convert -size 1500x1500 gradient:blue-green test-image-valid.png

# 有効なWebP（500KB）
convert -size 800x800 plasma: test-image-valid.webp

# サイズ超過（21MB）
convert -size 5000x5000 plasma: -quality 100 test-image-too-large.jpg

# 最大サイズ近く（19.5MB）
convert -size 4800x4800 plasma: -quality 95 test-image-max.jpg

# 境界値テスト用（20.0MB）
convert -size 4900x4900 plasma: -quality 95 test-image-20mb.jpg

# 境界値テスト用（20.1MB）
convert -size 4950x4950 plasma: -quality 95 test-image-20.1mb.jpg
```

---

## Playwrightテストコード例

### TC-001の実装例

```typescript
// tests/ad-checker.spec.ts
import { test, expect } from '@playwright/test';

test.describe('AdChecker E2E Tests', () => {
  test.beforeEach(async ({ page }) => {
    await page.goto('http://localhost:3247/');
  });

  test('[TC-001] ページ初期表示 @critical', async ({ page }) => {
    // タイトル確認
    await expect(page.locator('h1')).toContainText('メタ広告審査チェッカー');

    // 入力フィールド確認
    await expect(page.locator('label:has-text("見出し（任意）")')).toBeVisible();
    await expect(page.locator('label:has-text("説明文（任意）")')).toBeVisible();
    await expect(page.locator('label:has-text("CTA（任意）")')).toBeVisible();

    // アップロードエリア確認
    await expect(page.locator('text=画像をドラッグ&ドロップ')).toBeVisible();

    // ボタン無効化確認
    const submitButton = page.locator('button:has-text("AIチェック実行")');
    await expect(submitButton).toBeDisabled();

    // 結果エリア非表示確認
    await expect(page.locator('text=総合審査スコア')).not.toBeVisible();

    // 注意文確認
    await expect(page.locator('text=テキストまたは画像の少なくとも1つが必要です')).toBeVisible();
  });

  test('[TC-002] テキストのみで広告チェック実行（承認パターン） @critical', async ({ page }) => {
    // 入力
    await page.fill('label:has-text("見出し（任意）") >> input', '今すぐダウンロード');
    await page.fill('label:has-text("説明文（任意）") >> textarea', 'お手頃価格で高品質なサービスを提供します');
    await page.fill('label:has-text("CTA（任意）") >> input', '詳細を見る');

    // ボタン活性化確認
    const submitButton = page.locator('button:has-text("AIチェック実行")');
    await expect(submitButton).toBeEnabled();

    // チェック実行
    await submitButton.click();

    // ローディング状態確認
    await expect(page.locator('button:has-text("審査チェック中...")')).toBeVisible();
    await expect(page.locator('[role="progressbar"]')).toBeVisible();

    // 結果表示確認（最大5秒待機）
    await expect(page.locator('text=85%')).toBeVisible({ timeout: 5000 });
    await expect(page.locator('text=総合審査スコア')).toBeVisible();
    await expect(page.locator('text=承認される可能性が高い')).toBeVisible();

    // 問題箇所確認
    await expect(page.locator('text=問題箇所の指摘')).toBeVisible();
    await expect(page.locator('text=画像内テキスト量')).toBeVisible();

    // 改善提案確認
    await expect(page.locator('text=改善提案（コピペで使えます）')).toBeVisible();
    await expect(page.locator('text=修正前')).toBeVisible();
    await expect(page.locator('text=修正後')).toBeVisible();

    // 詳細情報確認
    await expect(page.locator('text=詳細情報')).toBeVisible();
    await expect(page.locator('text=92%')).toBeVisible(); // 信頼度
    await expect(page.locator('text=なし')).toBeVisible(); // NSFW検出

    // 再チェックボタン確認
    await expect(page.locator('button:has-text("修正内容を再チェック")')).toBeVisible();
  });

  test('[TC-005] 画像のみで広告チェック実行 @high', async ({ page }) => {
    // ファイル選択
    await page.setInputFiles('input[type="file"]', 'tests/fixtures/test-image-valid.jpg');

    // プレビュー表示確認
    await expect(page.locator('img[alt="プレビュー"]')).toBeVisible();
    await expect(page.locator('button:has([data-testid="DeleteIcon"])')).toBeVisible();

    // ボタン活性化確認
    const submitButton = page.locator('button:has-text("AIチェック実行")');
    await expect(submitButton).toBeEnabled();

    // チェック実行
    await submitButton.click();

    // 結果表示確認
    await expect(page.locator('text=総合審査スコア')).toBeVisible({ timeout: 5000 });
    await expect(page.locator('text=画像内テキスト量')).toBeVisible();
  });

  test('[TC-102] ファイルサイズ超過（21MB） @critical', async ({ page }) => {
    // 大きなファイルをアップロード
    await page.setInputFiles('input[type="file"]', 'tests/fixtures/test-image-too-large.jpg');

    // エラーメッセージ確認
    await expect(page.locator('text=ファイルサイズは20MB以下にしてください')).toBeVisible();

    // プレビュー非表示確認
    await expect(page.locator('img[alt="プレビュー"]')).not.toBeVisible();

    // ボタン無効化確認
    await expect(page.locator('button:has-text("AIチェック実行")')).toBeDisabled();
  });

  test('[TC-301] XSS攻撃（スクリプトタグ） @critical', async ({ page }) => {
    // XSS攻撃文字列を入力
    await page.fill('label:has-text("見出し（任意）") >> input', '<script>alert("XSS")</script>');
    await page.fill('label:has-text("説明文（任意）") >> textarea', 'テスト説明文');

    // チェック実行
    await page.click('button:has-text("AIチェック実行")');

    // 結果表示
    await expect(page.locator('text=総合審査スコア')).toBeVisible({ timeout: 5000 });

    // スクリプトが実行されていないことを確認
    // エスケープされたタグが文字列として表示されることを確認
    const violationText = await page.locator('text=<script>').textContent();
    expect(violationText).toContain('<script>'); // HTMLとして解釈されていない
  });

  test('[TC-403] モバイル表示（375x667） @critical', async ({ page }) => {
    // ビューポート設定
    await page.setViewportSize({ width: 375, height: 667 });

    // タイトルサイズ確認
    const title = page.locator('h1');
    const fontSize = await title.evaluate(el => window.getComputedStyle(el).fontSize);
    expect(fontSize).toBe('40px'); // 2.5rem

    // 詳細情報グリッド確認（結果表示後）
    await page.fill('label:has-text("見出し（任意）") >> input', 'テスト');
    await page.click('button:has-text("AIチェック実行")');
    await expect(page.locator('text=総合審査スコア')).toBeVisible({ timeout: 5000 });

    const grid = page.locator('div:has(> div:has-text("信頼度"))').first();
    const gridColumns = await grid.evaluate(el => window.getComputedStyle(el).gridTemplateColumns);
    expect(gridColumns).toContain('1fr'); // 1カラム表示

    // 横スクロール非発生確認
    const bodyWidth = await page.evaluate(() => document.body.scrollWidth);
    const windowWidth = await page.evaluate(() => window.innerWidth);
    expect(bodyWidth).toBeLessThanOrEqual(windowWidth);
  });
});
```

---

## テスト環境セットアップ

### Playwrightインストール

```bash
# Playwrightインストール
npm install -D @playwright/test

# ブラウザインストール
npx playwright install

# VSCode拡張機能（推奨）
# Playwright Test for VSCode をインストール
```

### playwright.config.ts

```typescript
import { defineConfig, devices } from '@playwright/test';

export default defineConfig({
  testDir: './tests',
  fullyParallel: true,
  forbidOnly: !!process.env.CI,
  retries: process.env.CI ? 2 : 0,
  workers: process.env.CI ? 1 : undefined,
  reporter: 'html',
  use: {
    baseURL: 'http://localhost:3247',
    trace: 'on-first-retry',
  },

  projects: [
    {
      name: 'chromium',
      use: { ...devices['Desktop Chrome'] },
    },

    {
      name: 'firefox',
      use: { ...devices['Desktop Firefox'] },
    },

    {
      name: 'webkit',
      use: { ...devices['Desktop Safari'] },
    },

    // モバイルテスト
    {
      name: 'Mobile Chrome',
      use: { ...devices['Pixel 5'] },
    },
    {
      name: 'Mobile Safari',
      use: { ...devices['iPhone 12'] },
    },
  ],

  webServer: {
    command: 'npm run dev',
    url: 'http://localhost:3247',
    reuseExistingServer: !process.env.CI,
  },
});
```

---

## テスト実行コマンド

```bash
# すべてのテストを実行
npx playwright test

# Criticalテストのみ実行
npx playwright test --grep "@critical"

# Highテストのみ実行
npx playwright test --grep "@high"

# 特定のテストケースを実行
npx playwright test --grep "TC-001"

# UI モードで実行（デバッグ用）
npx playwright test --ui

# レポート表示
npx playwright show-report

# ヘッドフルモード（ブラウザ表示）
npx playwright test --headed

# 特定のブラウザのみ
npx playwright test --project=chromium
```

---

## トラブルシューティング

### よくある問題

#### 1. ボタンが見つからない

```typescript
// NG: テキストが完全一致しない
await page.click('button:has-text("AIチェック")');

// OK: 部分一致
await page.click('button:has-text("AIチェック実行")');
```

#### 2. タイムアウトエラー

```typescript
// デフォルト30秒だが、APIが遅い場合は延長
await expect(page.locator('text=総合審査スコア')).toBeVisible({ timeout: 60000 });
```

#### 3. 画像アップロードが失敗

```typescript
// ファイルパスは絶対パスまたはテストディレクトリからの相対パスを使用
await page.setInputFiles('input[type="file"]', path.resolve(__dirname, 'fixtures/test-image.jpg'));
```

---

## まとめ

本E2Eテスト仕様書では、AdCheckerページの機能を網羅的にテストするための115のテストケースを定義しました。

### テストカバレッジ

- **正常系**: 15ケース（基本機能）
- **異常系**: 15ケース（エラーハンドリング）
- **バリデーション**: 10ケース（入力検証）
- **セキュリティ**: 5ケース（脆弱性対策）
- **レスポンシブ**: 10ケース（画面サイズ対応）
- **パフォーマンス**: 5ケース（速度・負荷）

### 推奨実行頻度

- **毎回のCI/CD**: Criticalテスト（8ケース）
- **プルリクエスト時**: Critical + Highテスト（22ケース）
- **週次実行**: Critical + High + Mediumテスト（44ケース）
- **リリース前**: 全テスト（115ケース）

### 次のステップ

1. Playwrightのセットアップ
2. テストデータ（画像ファイル）の準備
3. Criticalテストケースの実装
4. CI/CDパイプラインへの統合
5. Phase 11拡張時のテスト追加（認証、DB、レート制限等）

---

**最終更新日**: 2025-11-22
**バージョン**: 1.0（MVP対応）
**次回レビュー予定**: Phase 11拡張時
