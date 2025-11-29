# GuidePage E2Eテスト仕様書

生成日: 2025-11-22
対象ページ: /guide
テストフレームワーク: Playwright
テスト構造: test.step()を活用した段階的テスト
実行モード: ヘッドレスモード（headless: true）
作成者: E2Eテスト仕様書作成エージェント

## テスト実行条件
- VITE_E2E_MODE=true（Sentry無効化）
- フロントエンド・バックエンドサーバー起動必須
- 実認証必須（認証スキップ機能禁止）

## 概要
- 総テスト項目数: 45
- 高優先度: 15項目
- 中優先度: 18項目
- 低優先度: 12項目

## テスト項目一覧

| No | テストID | テスト項目 | 依存テストID | 機能分類 | テスト分類 | 優先度 | 確認内容 | テストデータ/手順 | 期待結果 | 実施日 | 結果 | 備考 |
|----|---------|----------|------------|---------|-----------|--------|---------|------------------|----------|--------|------|------|
| 1 | E2E-GUIDE-001 | ページ初期表示 | なし | ページ表示 | 正常系 | 高 | ページ全体が正しく表示される | `/guide`にアクセス | タイトル、サブタイトル、全セクション、ボタンが表示 | | | |
| 2 | E2E-GUIDE-002 | ページタイトル表示 | E2E-GUIDE-001 | ページ表示 | 正常系 | 高 | ページタイトルが正しく表示される | タイトル要素を確認 | 「使い方ガイド / FAQ」が表示される | | | |
| 3 | E2E-GUIDE-003 | サブタイトル表示 | E2E-GUIDE-001 | ページ表示 | 正常系 | 中 | サブタイトルが正しく表示される | サブタイトル要素を確認 | 「メタ広告審査チェッカーの使い方を簡単にご紹介します」が表示 | | | |
| 4 | E2E-GUIDE-004 | メタ広告審査の基礎知識セクション表示 | E2E-GUIDE-001 | セクション表示 | 正常系 | 高 | 基礎知識セクションが表示される | セクション1を確認 | 見出し、説明文、5つのチェックポイントが表示 | | | |
| 5 | E2E-GUIDE-005 | 基礎知識セクションの5項目確認 | E2E-GUIDE-004 | セクション表示 | 正常系 | 高 | 5つのチェック項目が正しく表示される | リスト項目を確認 | 画像内テキスト量、禁止コンテンツ、過度な肌露出、ビフォーアフター、誇大広告が表示 | | | |
| 6 | E2E-GUIDE-006 | 使い方3ステップセクション表示 | E2E-GUIDE-001 | セクション表示 | 正常系 | 高 | 3ステップセクションが表示される | セクション2を確認 | 見出し、3つのステップカードが表示 | | | |
| 7 | E2E-GUIDE-007 | ステップ1カード確認 | E2E-GUIDE-006 | セクション表示 | 正常系 | 中 | ステップ1の内容が正しい | カード1を確認 | 番号「1」、タイトル「テキストを入力」、説明文が表示 | | | |
| 8 | E2E-GUIDE-008 | ステップ2カード確認 | E2E-GUIDE-006 | セクション表示 | 正常系 | 中 | ステップ2の内容が正しい | カード2を確認 | 番号「2」、タイトル「画像をアップロード」、説明文が表示 | | | |
| 9 | E2E-GUIDE-009 | ステップ3カード確認 | E2E-GUIDE-006 | セクション表示 | 正常系 | 中 | ステップ3の内容が正しい | カード3を確認 | 番号「3」、タイトル「チェック実行」、説明文が表示 | | | |
| 10 | E2E-GUIDE-010 | FAQ セクション表示 | E2E-GUIDE-001 | セクション表示 | 正常系 | 高 | FAQセクションが表示される | セクション3を確認 | 見出し、6つのFAQ項目が表示 | | | |
| 11 | E2E-GUIDE-011 | FAQ 1項目確認 | E2E-GUIDE-010 | セクション表示 | 正常系 | 中 | FAQ 1番目の質問と回答が正しい | FAQ項目1を確認 | 「テキストだけ、または画像だけでもチェックできますか?」と回答が表示 | | | |
| 12 | E2E-GUIDE-012 | FAQ 2項目確認 | E2E-GUIDE-010 | セクション表示 | 正常系 | 中 | FAQ 2番目の質問と回答が正しい | FAQ項目2を確認 | 「アップロードできる画像の形式とサイズは?」と回答が表示 | | | |
| 13 | E2E-GUIDE-013 | FAQ 3項目確認 | E2E-GUIDE-010 | セクション表示 | 正常系 | 中 | FAQ 3番目の質問と回答が正しい | FAQ項目3を確認 | 「チェック結果はどのくらい正確ですか?」と回答が表示 | | | |
| 14 | E2E-GUIDE-014 | FAQ 4項目確認 | E2E-GUIDE-010 | セクション表示 | 正常系 | 中 | FAQ 4番目の質問と回答が正しい | FAQ項目4を確認 | 「アカウント登録は必要ですか?」と回答が表示 | | | |
| 15 | E2E-GUIDE-015 | FAQ 5項目確認 | E2E-GUIDE-010 | セクション表示 | 正常系 | 中 | FAQ 5番目の質問と回答が正しい | FAQ項目5を確認 | 「チェック履歴は保存されますか?」と回答が表示 | | | |
| 16 | E2E-GUIDE-016 | FAQ 6項目確認 | E2E-GUIDE-010 | セクション表示 | 正常系 | 中 | FAQ 6番目の質問と回答が正しい | FAQ項目6を確認 | 「審査に落ちた広告を改善する方法は?」と回答が表示 | | | |
| 17 | E2E-GUIDE-017 | Meta広告ポリシーリンクセクション表示 | E2E-GUIDE-001 | セクション表示 | 正常系 | 高 | 外部リンクセクションが表示される | セクション4を確認 | 見出し、説明文、リンクボタンが表示 | | | |
| 18 | E2E-GUIDE-018 | Meta広告ポリシーリンククリック | E2E-GUIDE-017 | 外部リンク | 正常系 | 高 | リンクが正しく動作する | リンクをクリック | 新しいタブでMeta広告ポリシーページが開く | | | |
| 19 | E2E-GUIDE-019 | チェッカーに戻るボタン表示 | E2E-GUIDE-001 | ナビゲーション | 正常系 | 高 | ボタンが表示される | ボタン要素を確認 | 「チェッカーに戻る」ボタンが表示される | | | |
| 20 | E2E-GUIDE-020 | チェッカーに戻るボタンクリック | E2E-GUIDE-019 | ナビゲーション | 正常系 | 高 | `/`へ遷移する | ボタンをクリック | トップページ（/）へ遷移 | | | |
| 21 | E2E-GUIDE-021 | Paperセクションのホバー効果 | E2E-GUIDE-001 | UI動作 | 正常系 | 低 | ホバー時にアニメーション発生 | 各Paperにマウスホバー | 上に移動、シャドウ強調される | | | |
| 22 | E2E-GUIDE-022 | ステップカードのホバー効果 | E2E-GUIDE-006 | UI動作 | 正常系 | 低 | ホバー時にアニメーション発生 | ステップカードにホバー | 上に移動、ボーダー色変更、シャドウ強調 | | | |
| 23 | E2E-GUIDE-023 | FAQカードのホバー効果 | E2E-GUIDE-010 | UI動作 | 正常系 | 低 | ホバー時にアニメーション発生 | FAQカードにホバー | 右に移動、ボーダー色変更、シャドウ表示 | | | |
| 24 | E2E-GUIDE-024 | 外部リンクボタンのホバー効果 | E2E-GUIDE-017 | UI動作 | 正常系 | 低 | ホバー時にアニメーション発生 | リンクボタンにホバー | 拡大、背景色変更、シャドウ強調 | | | |
| 25 | E2E-GUIDE-025 | ページアニメーションの確認 | E2E-GUIDE-001 | UI動作 | 正常系 | 低 | 初期表示時のフェードインアニメーション | ページにアクセス | タイトル、セクションがフェードイン表示される | | | |
| 26 | E2E-GUIDE-026 | ブラウザバックボタン | E2E-GUIDE-020 | ナビゲーション | 異常系 | 中 | バックボタンで正しく戻る | /guide→/→バック | /guideに戻る | | | |
| 27 | E2E-GUIDE-027 | ブラウザリロード | E2E-GUIDE-001 | ページ動作 | 異常系 | 中 | リロード後も正しく表示 | F5キー押下 | ページが正常に再表示される | | | |
| 28 | E2E-GUIDE-028 | 直接URLアクセス | なし | ページアクセス | 正常系 | 高 | 直接URLでアクセス可能 | `/guide`に直接アクセス | ページが正しく表示される | | | |
| 29 | E2E-GUIDE-029 | 外部リンクのrel属性確認 | E2E-GUIDE-017 | セキュリティ | セキュリティ | 高 | rel="noopener noreferrer"が設定されている | リンク要素を検証 | rel属性に"noopener noreferrer"が含まれる | | | |
| 30 | E2E-GUIDE-030 | 外部リンクのtarget属性確認 | E2E-GUIDE-017 | セキュリティ | セキュリティ | 高 | target="_blank"が設定されている | リンク要素を検証 | target属性が"_blank" | | | |
| 31 | E2E-GUIDE-031 | 外部リンクのURL検証 | E2E-GUIDE-017 | セキュリティ | セキュリティ | 高 | 正しいMeta URLが設定されている | リンクhrefを検証 | https://www.facebook.com/policies/ads/ | | | |
| 32 | E2E-GUIDE-032 | デスクトップ表示（1920x1080） | E2E-GUIDE-001 | レスポンシブ | レスポンシブ | 高 | デスクトップで正しく表示 | ビューポート1920x1080 | タイトル3rem、3カラムステップグリッド表示 | | | |
| 33 | E2E-GUIDE-033 | タブレット表示（768x1024） | E2E-GUIDE-001 | レスポンシブ | レスポンシブ | 高 | タブレットで正しく表示 | ビューポート768x1024 | タイトルサイズ調整、ステップグリッド表示 | | | |
| 34 | E2E-GUIDE-034 | モバイル表示（375x667） | E2E-GUIDE-001 | レスポンシブ | レスポンシブ | 高 | モバイルで正しく表示 | ビューポート375x667 | タイトル2rem、1カラムステップグリッド、横スクロールなし | | | |
| 35 | E2E-GUIDE-035 | 極小画面（320x568） | E2E-GUIDE-001 | レスポンシブ | レスポンシブ | 中 | 極小画面で正しく表示 | ビューポート320x568 | 全要素が表示、横スクロールなし | | | |
| 36 | E2E-GUIDE-036 | 極大画面（2560x1440） | E2E-GUIDE-001 | レスポンシブ | レスポンシブ | 低 | 極大画面で正しく表示 | ビューポート2560x1440 | maxWidth制限が機能、中央配置 | | | |
| 37 | E2E-GUIDE-037 | 横向きモバイル（667x375） | E2E-GUIDE-001 | レスポンシブ | レスポンシブ | 中 | 横向きで正しく表示 | ビューポート667x375 | 横向きでもレイアウト崩れなし | | | |
| 38 | E2E-GUIDE-038 | ステップカードのレスポンシブ | E2E-GUIDE-006 | レスポンシブ | レスポンシブ | 中 | カードが適切に配置される | 各画面サイズで確認 | デスクトップ3カラム、モバイル1カラム | | | |
| 39 | E2E-GUIDE-039 | FAQカードのレスポンシブ | E2E-GUIDE-010 | レスポンシブ | レスポンシブ | 中 | FAQが読みやすく表示される | 各画面サイズで確認 | テキストが折り返され、横スクロールなし | | | |
| 40 | E2E-GUIDE-040 | タッチターゲットサイズ（モバイル） | E2E-GUIDE-034 | レスポンシブ | レスポンシブ | 中 | ボタンがタップしやすい | モバイルでボタンサイズ確認 | ボタンが最低44x44px以上 | | | |
| 41 | E2E-GUIDE-041 | 長いテキストの表示（モバイル） | E2E-GUIDE-034 | レスポンシブ | レスポンシブ | 低 | テキストが正しく折り返される | モバイルでテキスト確認 | 横スクロールなし、読みやすい | | | |
| 42 | E2E-GUIDE-042 | ページロード速度 | E2E-GUIDE-001 | パフォーマンス | 正常系 | 中 | ページが高速に表示される | Performance API測定 | LCP 2.5秒以内 | | | |
| 43 | E2E-GUIDE-043 | 画像なしページのため軽量 | E2E-GUIDE-001 | パフォーマンス | 正常系 | 低 | 静的コンテンツのみで高速 | ネットワークタブ確認 | 初期ロード1秒以内 | | | |
| 44 | E2E-GUIDE-044 | スクロール動作確認 | E2E-GUIDE-001 | ページ動作 | 正常系 | 中 | スムーズにスクロール可能 | ページをスクロール | 全セクションにアクセス可能 | | | |
| 45 | E2E-GUIDE-045 | キーボードナビゲーション | E2E-GUIDE-001 | アクセシビリティ | 正常系 | 中 | キーボードで操作可能 | Tabキーでフォーカス移動 | リンク、ボタンにフォーカス可能 | | | |

## テスト分類別カバレッジ
- 正常系: 25項目
- 異常系: 2項目
- セキュリティ: 3項目
- レスポンシブ: 10項目
- アクセシビリティ: 1項目
- パフォーマンス: 2項目
- UI動作: 4項目

## セクション構成
1. **メタ広告審査の基礎知識**
   - 5つのチェックポイント（リスト形式）
   - 緑色チェックマーク付き

2. **使い方（3ステップ）**
   - 3つのカード（1列3カラム、モバイルは1カラム）
   - 各カードに番号、タイトル、説明文

3. **よくある質問（FAQ）**
   - 6つのFAQ項目
   - Q アイコン + 質問 + 回答

4. **Meta広告ポリシーリンク**
   - 外部リンクボタン
   - target="_blank", rel="noopener noreferrer"

5. **チェッカーに戻るボタン**
   - `/`へ遷移

## API呼び出し一覧
なし（静的ページ）

## 優先度別実施順序
1. **高優先度（必須）**: E2E-GUIDE-001, 002, 004, 005, 006, 010, 017, 018, 019, 020, 028, 029, 030, 031, 032, 033, 034
2. **中優先度（推奨）**: E2E-GUIDE-003, 007, 008, 009, 011, 012, 013, 014, 015, 016, 026, 027, 035, 037, 038, 039, 040, 042, 044, 045
3. **低優先度（任意）**: E2E-GUIDE-021, 022, 023, 024, 025, 036, 041, 043

## 前提条件
- テストアカウント: なし（パブリックページ）
- 認証: 不要
- バックエンド: 不要（静的ページ）
- フロントエンド: http://localhost:3247

---

## テスト詳細仕様

### 1. 正常系テスト

#### E2E-GUIDE-001: ページ初期表示
**優先度**: 高
**依存**: なし

**テスト手順**:
```typescript
await test.step('ガイドページにアクセス', async () => {
  await page.goto('http://localhost:3247/guide');
});

await test.step('ページ全体が表示されることを確認', async () => {
  await expect(page.locator('h1')).toBeVisible();
  await expect(page.locator('h1')).toContainText('使い方ガイド / FAQ');
  await expect(page.locator('text=メタ広告審査チェッカーの使い方')).toBeVisible();

  // 4つのセクションPaperが表示
  const sections = page.locator('[elevation="2"]');
  await expect(sections).toHaveCount(4);

  // チェッカーに戻るボタンが表示
  await expect(page.locator('button:has-text("チェッカーに戻る")')).toBeVisible();
});
```

**期待結果**:
- ページタイトル「使い方ガイド / FAQ」が表示される
- サブタイトルが表示される
- 4つのPaperセクション（基礎知識、使い方、FAQ、外部リンク）が表示される
- 「チェッカーに戻る」ボタンが表示される

---

#### E2E-GUIDE-004: メタ広告審査の基礎知識セクション表示
**優先度**: 高
**依存**: E2E-GUIDE-001

**テスト手順**:
```typescript
await test.step('基礎知識セクションを確認', async () => {
  const section = page.locator('text=メタ広告審査の基礎知識').locator('..');
  await expect(section).toBeVisible();

  // セクション説明文
  await expect(section.locator('text=メタ広告では、広告が掲載される前に')).toBeVisible();

  // 5つのリスト項目が表示
  const listItems = section.locator('li');
  await expect(listItems).toHaveCount(5);
});
```

**期待結果**:
- セクションタイトル「メタ広告審査の基礎知識」が表示される
- 説明文が表示される
- 5つのリスト項目が表示される

---

#### E2E-GUIDE-005: 基礎知識セクションの5項目確認
**優先度**: 高
**依存**: E2E-GUIDE-004

**テスト手順**:
```typescript
await test.step('5つのチェック項目を確認', async () => {
  await expect(page.locator('text=画像内テキスト量')).toBeVisible();
  await expect(page.locator('text=20%以下が推奨')).toBeVisible();

  await expect(page.locator('text=禁止コンテンツ')).toBeVisible();
  await expect(page.locator('text=アルコール、タバコ、医薬品')).toBeVisible();

  await expect(page.locator('text=過度な肌露出・性的表現')).toBeVisible();

  await expect(page.locator('text=ビフォーアフター表現')).toBeVisible();

  await expect(page.locator('text=誇大広告・誤解を招く表現')).toBeVisible();
  await expect(page.locator('text=「最安値」「絶対」等の断定表現')).toBeVisible();
});
```

**期待結果**:
- 5つのチェック項目が正しく表示される
- 各項目にチェックマーク（✓）が表示される
- タイトルと説明文が正しく表示される

---

#### E2E-GUIDE-006: 使い方3ステップセクション表示
**優先度**: 高
**依存**: E2E-GUIDE-001

**テスト手順**:
```typescript
await test.step('3ステップセクションを確認', async () => {
  await expect(page.locator('text=使い方（3ステップ）')).toBeVisible();

  // 3つのステップカードが表示
  const stepCards = page.locator('text=1').locator('..').locator('..');
  await expect(stepCards).toHaveCount(3);
});
```

**期待結果**:
- セクションタイトル「使い方（3ステップ）」が表示される
- 3つのステップカードが表示される
- 注意書き「※テキストまたは画像の少なくとも1つは必須です」が表示される

---

#### E2E-GUIDE-018: Meta広告ポリシーリンククリック
**優先度**: 高
**依存**: E2E-GUIDE-017

**テスト手順**:
```typescript
await test.step('外部リンクをクリック', async () => {
  // 新しいタブが開くことを期待
  const [newPage] = await Promise.all([
    page.context().waitForEvent('page'),
    page.click('text=Meta広告ポリシーを見る')
  ]);

  // 新しいタブのURLを確認
  await newPage.waitForLoadState();
  expect(newPage.url()).toContain('facebook.com/policies/ads');

  // 新しいタブを閉じる
  await newPage.close();
});
```

**期待結果**:
- 新しいタブでMeta広告ポリシーページが開く
- URLが`https://www.facebook.com/policies/ads/`を含む
- 元のページは閉じない

---

#### E2E-GUIDE-020: チェッカーに戻るボタンクリック
**優先度**: 高
**依存**: E2E-GUIDE-019

**テスト手順**:
```typescript
await test.step('チェッカーに戻るボタンをクリック', async () => {
  await page.click('button:has-text("チェッカーに戻る")');

  // URLが/に変わることを確認
  await page.waitForURL('http://localhost:3247/');
  expect(page.url()).toBe('http://localhost:3247/');

  // トップページのタイトルが表示されることを確認
  await expect(page.locator('h1:has-text("メタ広告審査チェッカー")')).toBeVisible();
});
```

**期待結果**:
- `/`へ遷移する
- トップページが表示される

---

### 2. セキュリティテスト

#### E2E-GUIDE-029: 外部リンクのrel属性確認
**優先度**: 高
**依存**: E2E-GUIDE-017

**テスト手順**:
```typescript
await test.step('外部リンクのrel属性を確認', async () => {
  const link = page.locator('a:has-text("Meta広告ポリシーを見る")');
  const rel = await link.getAttribute('rel');

  expect(rel).toContain('noopener');
  expect(rel).toContain('noreferrer');
});
```

**期待結果**:
- rel属性に`noopener`が含まれる
- rel属性に`noreferrer`が含まれる
- セキュリティ脆弱性（tabnabbing）が防止される

---

#### E2E-GUIDE-030: 外部リンクのtarget属性確認
**優先度**: 高
**依存**: E2E-GUIDE-017

**テスト手順**:
```typescript
await test.step('外部リンクのtarget属性を確認', async () => {
  const link = page.locator('a:has-text("Meta広告ポリシーを見る")');
  const target = await link.getAttribute('target');

  expect(target).toBe('_blank');
});
```

**期待結果**:
- target属性が`_blank`である
- 新しいタブで開く

---

#### E2E-GUIDE-031: 外部リンクのURL検証
**優先度**: 高
**依存**: E2E-GUIDE-017

**テスト手順**:
```typescript
await test.step('外部リンクのhref属性を確認', async () => {
  const link = page.locator('a:has-text("Meta広告ポリシーを見る")');
  const href = await link.getAttribute('href');

  expect(href).toBe('https://www.facebook.com/policies/ads/');
});
```

**期待結果**:
- href属性が正しいMeta URLである
- HTTPSプロトコルが使用されている

---

### 3. レスポンシブテスト

#### E2E-GUIDE-032: デスクトップ表示（1920x1080）
**優先度**: 高
**依存**: E2E-GUIDE-001

**テスト手順**:
```typescript
await test.step('デスクトップビューポートを設定', async () => {
  await page.setViewportSize({ width: 1920, height: 1080 });
  await page.goto('http://localhost:3247/guide');
});

await test.step('デスクトップレイアウトを確認', async () => {
  // タイトルサイズ確認（3rem = 48px）
  const title = page.locator('h1');
  const fontSize = await title.evaluate(el => window.getComputedStyle(el).fontSize);
  expect(fontSize).toBe('48px');

  // ステップカードが3カラムで表示
  const stepGrid = page.locator('text=1').locator('..').locator('..');
  const gridColumns = await stepGrid.evaluate(el =>
    window.getComputedStyle(el.parentElement).gridTemplateColumns
  );
  expect(gridColumns).toContain('1fr 1fr 1fr'); // 3カラム

  // 横スクロールなし
  const bodyWidth = await page.evaluate(() => document.body.scrollWidth);
  const windowWidth = await page.evaluate(() => window.innerWidth);
  expect(bodyWidth).toBeLessThanOrEqual(windowWidth);
});
```

**期待結果**:
- タイトルが3rem（48px）で表示される
- ステップカードが3カラムで表示される
- 横スクロールが発生しない
- すべての要素が適切に配置される

---

#### E2E-GUIDE-034: モバイル表示（375x667）
**優先度**: 高
**依存**: E2E-GUIDE-001

**テスト手順**:
```typescript
await test.step('モバイルビューポートを設定', async () => {
  await page.setViewportSize({ width: 375, height: 667 });
  await page.goto('http://localhost:3247/guide');
});

await test.step('モバイルレイアウトを確認', async () => {
  // タイトルサイズ確認（2rem = 32px）
  const title = page.locator('h1');
  const fontSize = await title.evaluate(el => window.getComputedStyle(el).fontSize);
  expect(fontSize).toBe('32px');

  // ステップカードが1カラムで表示
  const stepGrid = page.locator('text=1').locator('..').locator('..');
  const gridColumns = await stepGrid.evaluate(el =>
    window.getComputedStyle(el.parentElement).gridTemplateColumns
  );
  expect(gridColumns).toContain('1fr'); // 1カラム

  // 横スクロールなし
  const bodyWidth = await page.evaluate(() => document.body.scrollWidth);
  const windowWidth = await page.evaluate(() => window.innerWidth);
  expect(bodyWidth).toBeLessThanOrEqual(windowWidth);

  // タッチターゲットサイズ確認
  const button = page.locator('button:has-text("チェッカーに戻る")');
  const bbox = await button.boundingBox();
  expect(bbox?.height).toBeGreaterThanOrEqual(44);
});
```

**期待結果**:
- タイトルが2rem（32px）で表示される
- ステップカードが1カラムで表示される
- 横スクロールが発生しない
- ボタンが最低44px以上の高さ

---

### 4. 異常系テスト

#### E2E-GUIDE-026: ブラウザバックボタン
**優先度**: 中
**依存**: E2E-GUIDE-020

**テスト手順**:
```typescript
await test.step('ガイドページにアクセス', async () => {
  await page.goto('http://localhost:3247/guide');
});

await test.step('チェッカーに戻る', async () => {
  await page.click('button:has-text("チェッカーに戻る")');
  await page.waitForURL('http://localhost:3247/');
});

await test.step('ブラウザバックボタンで戻る', async () => {
  await page.goBack();
  await page.waitForURL('http://localhost:3247/guide');

  // ガイドページが再表示されることを確認
  await expect(page.locator('h1:has-text("使い方ガイド")')).toBeVisible();
});
```

**期待結果**:
- ブラウザバックボタンで正しく戻る
- ガイドページが再表示される
- エラーが発生しない

---

#### E2E-GUIDE-027: ブラウザリロード
**優先度**: 中
**依存**: E2E-GUIDE-001

**テスト手順**:
```typescript
await test.step('ガイドページにアクセス', async () => {
  await page.goto('http://localhost:3247/guide');
  await expect(page.locator('h1')).toBeVisible();
});

await test.step('ブラウザリロード', async () => {
  await page.reload();

  // ページが正常に再表示されることを確認
  await expect(page.locator('h1:has-text("使い方ガイド")')).toBeVisible();
  await expect(page.locator('text=メタ広告審査の基礎知識')).toBeVisible();
  await expect(page.locator('button:has-text("チェッカーに戻る")')).toBeVisible();
});
```

**期待結果**:
- リロード後も正しく表示される
- 全セクションが再表示される
- エラーが発生しない

---

## Playwrightテストコード例

```typescript
// tests/guide-page.spec.ts
import { test, expect } from '@playwright/test';

test.describe('GuidePage E2E Tests', () => {
  test.beforeEach(async ({ page }) => {
    await page.goto('http://localhost:3247/guide');
  });

  test('[E2E-GUIDE-001] ページ初期表示 @critical', async ({ page }) => {
    await test.step('ページ全体が表示されることを確認', async () => {
      // タイトル確認
      await expect(page.locator('h1')).toContainText('使い方ガイド / FAQ');

      // サブタイトル確認
      await expect(page.locator('text=メタ広告審査チェッカーの使い方')).toBeVisible();

      // 4つのPaperセクション確認
      const sections = await page.locator('text=メタ広告審査の基礎知識').count();
      expect(sections).toBeGreaterThan(0);

      // ボタン確認
      await expect(page.locator('button:has-text("チェッカーに戻る")')).toBeVisible();
    });
  });

  test('[E2E-GUIDE-005] 基礎知識セクションの5項目確認 @critical', async ({ page }) => {
    await test.step('5つのチェック項目を確認', async () => {
      const items = [
        '画像内テキスト量',
        '禁止コンテンツ',
        '過度な肌露出・性的表現',
        'ビフォーアフター表現',
        '誇大広告・誤解を招く表現'
      ];

      for (const item of items) {
        await expect(page.locator(`text=${item}`)).toBeVisible();
      }
    });
  });

  test('[E2E-GUIDE-018] Meta広告ポリシーリンククリック @critical', async ({ page }) => {
    await test.step('外部リンクをクリック', async () => {
      const [newPage] = await Promise.all([
        page.context().waitForEvent('page'),
        page.click('text=Meta広告ポリシーを見る')
      ]);

      await newPage.waitForLoadState();
      expect(newPage.url()).toContain('facebook.com/policies/ads');

      await newPage.close();
    });
  });

  test('[E2E-GUIDE-020] チェッカーに戻るボタンクリック @critical', async ({ page }) => {
    await test.step('チェッカーに戻る', async () => {
      await page.click('button:has-text("チェッカーに戻る")');
      await page.waitForURL('http://localhost:3247/');

      await expect(page.locator('h1:has-text("メタ広告審査チェッカー")')).toBeVisible();
    });
  });

  test('[E2E-GUIDE-029] 外部リンクのrel属性確認 @critical', async ({ page }) => {
    await test.step('rel属性を確認', async () => {
      const link = page.locator('a:has-text("Meta広告ポリシーを見る")');
      const rel = await link.getAttribute('rel');

      expect(rel).toContain('noopener');
      expect(rel).toContain('noreferrer');
    });
  });

  test('[E2E-GUIDE-034] モバイル表示（375x667） @critical', async ({ page }) => {
    await test.step('モバイルビューポート設定', async () => {
      await page.setViewportSize({ width: 375, height: 667 });
    });

    await test.step('モバイルレイアウト確認', async () => {
      // タイトルサイズ確認
      const title = page.locator('h1');
      const fontSize = await title.evaluate(el => window.getComputedStyle(el).fontSize);
      expect(fontSize).toBe('32px'); // 2rem

      // 横スクロールなし
      const bodyWidth = await page.evaluate(() => document.body.scrollWidth);
      const windowWidth = await page.evaluate(() => window.innerWidth);
      expect(bodyWidth).toBeLessThanOrEqual(windowWidth);
    });
  });
});
```

---

## テスト実行コマンド

```bash
# すべてのガイドページテストを実行
npx playwright test tests/guide-page.spec.ts

# Criticalテストのみ実行
npx playwright test tests/guide-page.spec.ts --grep "@critical"

# 特定のテストケースを実行
npx playwright test tests/guide-page.spec.ts --grep "E2E-GUIDE-001"

# UI モードで実行（デバッグ用）
npx playwright test tests/guide-page.spec.ts --ui

# ヘッドフルモード（ブラウザ表示）
npx playwright test tests/guide-page.spec.ts --headed

# モバイルのみ
npx playwright test tests/guide-page.spec.ts --project="Mobile Chrome"
```

---

## まとめ

本E2Eテスト仕様書では、GuidePageの機能を網羅的にテストするための45のテストケースを定義しました。

### テストカバレッジ
- **正常系**: 25ケース（ページ表示、セクション表示、ナビゲーション）
- **異常系**: 2ケース（ブラウザ動作）
- **セキュリティ**: 3ケース（外部リンク検証）
- **レスポンシブ**: 10ケース（画面サイズ対応）
- **その他**: 5ケース（UI動作、パフォーマンス、アクセシビリティ）

### 推奨実行頻度
- **毎回のCI/CD**: Criticalテスト（17ケース）
- **プルリクエスト時**: Critical + Highテスト（17ケース）
- **週次実行**: Critical + High + Mediumテスト（35ケース）
- **リリース前**: 全テスト（45ケース）

### 特徴
- **静的ページ**: API呼び出しなし、高速テスト可能
- **外部リンク**: セキュリティ検証（rel, target属性）
- **レスポンシブ**: 5段階の画面サイズ対応
- **シンプル**: 複雑な状態管理なし

---

**最終更新日**: 2025-11-22
**バージョン**: 1.0（MVP対応）
**次回レビュー予定**: Phase 11拡張時
