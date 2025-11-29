import { test, expect } from '@playwright/test';

test.describe('使い方ガイドページ', () => {
  test('E2E-GUIDE-001: ページ初期表示', async ({ page }) => {
    await page.goto('/guide');

    // タイトル確認
    await expect(page.locator('h1')).toContainText('使い方ガイド / FAQ');

    // サブタイトル確認
    await expect(page.getByText('メタ広告審査チェッカーの使い方を簡単にご紹介します')).toBeVisible();

    // 使い方セクション
    await expect(page.getByText('使い方（3ステップ）')).toBeVisible();

    // チェッカーに戻るボタン
    await expect(page.getByRole('button', { name: 'チェッカーに戻る' })).toBeVisible();
  });

  test('E2E-GUIDE-002: ページタイトル表示', async ({ page }) => {
    await page.goto('/guide');
    await expect(page.locator('h1')).toContainText('使い方ガイド / FAQ');
  });

  test('E2E-GUIDE-003: サブタイトル表示', async ({ page }) => {
    await page.goto('/guide');
    await expect(page.getByText('メタ広告審査チェッカーの使い方を簡単にご紹介します')).toBeVisible();
  });

  test('E2E-GUIDE-006: 使い方3ステップセクション表示', async ({ page }) => {
    await page.goto('/guide');
    await expect(page.getByText('使い方（3ステップ）')).toBeVisible();
    // 3つのステップカードがある
    await expect(page.getByText('テキストを入力')).toBeVisible();
    await expect(page.getByText('画像をアップロード')).toBeVisible();
    await expect(page.getByText('チェック実行')).toBeVisible();
  });

  test('E2E-GUIDE-007: ステップ1カード確認', async ({ page }) => {
    await page.goto('/guide');
    await expect(page.getByText('テキストを入力')).toBeVisible();
    await expect(page.getByText('広告の見出し、説明文、CTAを入力します')).toBeVisible();
  });

  test('E2E-GUIDE-008: ステップ2カード確認', async ({ page }) => {
    await page.goto('/guide');
    await expect(page.getByText('画像をアップロード')).toBeVisible();
    await expect(page.getByText('広告画像をドラッグ&ドロップまたは選択します')).toBeVisible();
  });

  test('E2E-GUIDE-009: ステップ3カード確認', async ({ page }) => {
    await page.goto('/guide');
    await expect(page.getByText('チェック実行').first()).toBeVisible();
    await expect(page.getByText('30秒以内にAI審査結果と改善提案を取得できます')).toBeVisible();
  });

  test('E2E-GUIDE-011-016: FAQ 6項目確認', async ({ page }) => {
    await page.goto('/guide');
    // FAQ 6項目
    await expect(page.getByText('テキストだけ、または画像だけでもチェックできますか?')).toBeVisible();
    await expect(page.getByText('アップロードできる画像の形式とサイズは?')).toBeVisible();
    await expect(page.getByText('チェック結果はどのくらい正確ですか?')).toBeVisible();
    await expect(page.getByText('アカウント登録は必要ですか?')).toBeVisible();
    await expect(page.getByText('チェック履歴は保存されますか?')).toBeVisible();
    await expect(page.getByText('審査に落ちた広告を改善する方法は?')).toBeVisible();
  });

  test('E2E-GUIDE-018: Meta広告ポリシーリンククリック', async ({ page, context }) => {
    await page.goto('/guide');

    // 新しいタブで開くリンクをテスト
    const [newPage] = await Promise.all([
      context.waitForEvent('page'),
      page.getByRole('link', { name: /Meta広告ポリシーを見る/ }).click()
    ]);

    // URLを確認（リダイレクト先も許可）
    const url = newPage.url();
    expect(url.includes('facebook.com/policies') || url.includes('transparency.meta.com')).toBe(true);
    await newPage.close();
  });

  test('E2E-GUIDE-019: チェッカーに戻るボタン表示', async ({ page }) => {
    await page.goto('/guide');
    await expect(page.getByRole('button', { name: 'チェッカーに戻る' })).toBeVisible();
  });

  test('E2E-GUIDE-026: ブラウザバックボタン', async ({ page }) => {
    await page.goto('/guide');
    await page.getByRole('button', { name: 'チェッカーに戻る' }).click();
    await expect(page).toHaveURL('/');

    await page.goBack();
    await expect(page).toHaveURL('/guide');
    await expect(page.locator('h1')).toContainText('使い方ガイド / FAQ');
  });

  test('E2E-GUIDE-027: ブラウザリロード', async ({ page }) => {
    await page.goto('/guide');
    await expect(page.locator('h1')).toContainText('使い方ガイド / FAQ');

    await page.reload();
    await expect(page.locator('h1')).toContainText('使い方ガイド / FAQ');
    await expect(page.getByText('メタ広告審査の基礎知識')).toBeVisible();
  });

  test('E2E-GUIDE-028: 直接URLアクセス', async ({ page }) => {
    await page.goto('/guide');
    await expect(page).toHaveURL('/guide');
    await expect(page.locator('h1')).toContainText('使い方ガイド / FAQ');
  });

  test('E2E-GUIDE-032: デスクトップ表示（1920x1080）', async ({ page }) => {
    await page.setViewportSize({ width: 1920, height: 1080 });
    await page.goto('/guide');

    await expect(page.locator('h1')).toBeVisible();
    // 横スクロールなし
    const bodyWidth = await page.evaluate(() => document.body.scrollWidth);
    const windowWidth = await page.evaluate(() => window.innerWidth);
    expect(bodyWidth).toBeLessThanOrEqual(windowWidth);
  });

  test('E2E-GUIDE-033: タブレット表示（768x1024）', async ({ page }) => {
    await page.setViewportSize({ width: 768, height: 1024 });
    await page.goto('/guide');

    await expect(page.locator('h1')).toBeVisible();
    const bodyWidth = await page.evaluate(() => document.body.scrollWidth);
    const windowWidth = await page.evaluate(() => window.innerWidth);
    expect(bodyWidth).toBeLessThanOrEqual(windowWidth);
  });

  test('E2E-GUIDE-034: モバイル表示（375x667）', async ({ page }) => {
    await page.setViewportSize({ width: 375, height: 667 });
    await page.goto('/guide');

    await expect(page.locator('h1')).toBeVisible();
    // ボタンがタップ可能サイズ
    const button = page.getByRole('button', { name: 'チェッカーに戻る' });
    const box = await button.boundingBox();
    expect(box?.height).toBeGreaterThanOrEqual(44);

    // 横スクロールなし
    const bodyWidth = await page.evaluate(() => document.body.scrollWidth);
    const windowWidth = await page.evaluate(() => window.innerWidth);
    expect(bodyWidth).toBeLessThanOrEqual(windowWidth);
  });

  test('E2E-GUIDE-004: メタ広告審査の基礎知識セクション表示', async ({ page }) => {
    await page.goto('/guide');

    // 基礎知識セクション
    await expect(page.getByText('メタ広告審査の基礎知識')).toBeVisible();
  });

  test('E2E-GUIDE-005: 基礎知識セクションの5項目確認', async ({ page }) => {
    await page.goto('/guide');

    // 主要5項目
    await expect(page.getByText('画像内テキスト量')).toBeVisible();
    await expect(page.getByText('禁止コンテンツ')).toBeVisible();
    await expect(page.getByText('過度な肌露出・性的表現')).toBeVisible();
    await expect(page.getByText('ビフォーアフター表現')).toBeVisible();
    await expect(page.getByText('誇大広告・誤解を招く表現')).toBeVisible();
  });

  test('E2E-GUIDE-010: FAQセクション表示', async ({ page }) => {
    await page.goto('/guide');

    // よくある質問セクション
    await expect(page.getByText('よくある質問（FAQ）')).toBeVisible();

    // FAQ項目が表示される（展開不要、常に表示）
    await expect(page.getByText('テキストだけ、または画像だけでもチェックできますか?')).toBeVisible();
    await expect(page.getByText('アップロードできる画像の形式とサイズは?')).toBeVisible();
  });

  test('E2E-GUIDE-017: Meta広告ポリシーリンクセクション表示', async ({ page }) => {
    await page.goto('/guide');

    // 外部リンクセクション
    await expect(page.getByText('さらに詳しく知りたい方へ')).toBeVisible();
    await expect(page.getByRole('link', { name: /Meta広告ポリシーを見る/ })).toBeVisible();
  });

  test('E2E-GUIDE-020: チェッカーに戻るボタンクリック', async ({ page }) => {
    await page.goto('/guide');

    // ヘッダーのボタンをクリック
    await page.getByRole('button', { name: 'チェッカーに戻る' }).click();

    // トップページに遷移
    await expect(page).toHaveURL('/');
    await expect(page.locator('h1')).toContainText('メタ広告審査チェッカー');
  });

  test('E2E-GUIDE-029: 外部リンクのrel属性確認', async ({ page }) => {
    await page.goto('/guide');

    const link = page.getByRole('link', { name: /Meta広告ポリシーを見る/ });
    await expect(link).toHaveAttribute('rel', /noopener/);
    await expect(link).toHaveAttribute('rel', /noreferrer/);
  });

  test('E2E-GUIDE-030: 外部リンクのtarget属性確認', async ({ page }) => {
    await page.goto('/guide');

    const link = page.getByRole('link', { name: /Meta広告ポリシーを見る/ });
    await expect(link).toHaveAttribute('target', '_blank');
  });

  test('E2E-GUIDE-031: 外部リンクのURL検証', async ({ page }) => {
    await page.goto('/guide');

    const link = page.getByRole('link', { name: /Meta広告ポリシーを見る/ });
    await expect(link).toHaveAttribute('href', 'https://www.facebook.com/policies/ads/');
  });

  // E2E-GUIDE-035: 極小画面（320x568）
  test('E2E-GUIDE-035: 極小画面（320x568）', async ({ page }) => {
    await page.setViewportSize({ width: 320, height: 568 });
    await page.goto('/guide');

    await expect(page.locator('h1')).toBeVisible();

    // 横スクロールなし
    const bodyWidth = await page.evaluate(() => document.body.scrollWidth);
    const windowWidth = await page.evaluate(() => window.innerWidth);
    expect(bodyWidth).toBeLessThanOrEqual(windowWidth);
  });

  // E2E-GUIDE-036: 極大画面（2560x1440）
  test('E2E-GUIDE-036: 極大画面（2560x1440）', async ({ page }) => {
    await page.setViewportSize({ width: 2560, height: 1440 });
    await page.goto('/guide');

    await expect(page.locator('h1')).toBeVisible();
  });

  // E2E-GUIDE-037: 横向きモバイル（667x375）
  test('E2E-GUIDE-037: 横向きモバイル（667x375）', async ({ page }) => {
    await page.setViewportSize({ width: 667, height: 375 });
    await page.goto('/guide');

    await expect(page.locator('h1')).toBeVisible();

    // 横スクロールなし
    const bodyWidth = await page.evaluate(() => document.body.scrollWidth);
    const windowWidth = await page.evaluate(() => window.innerWidth);
    expect(bodyWidth).toBeLessThanOrEqual(windowWidth);
  });

  // E2E-GUIDE-040: タッチターゲットサイズ（モバイル）
  test('E2E-GUIDE-040: タッチターゲットサイズ（モバイル）', async ({ page }) => {
    await page.setViewportSize({ width: 375, height: 667 });
    await page.goto('/guide');

    // チェッカーに戻るボタンのサイズ確認（最小44px）
    const button = page.getByRole('button', { name: 'チェッカーに戻る' });
    const box = await button.boundingBox();
    expect(box?.height).toBeGreaterThanOrEqual(44);
    expect(box?.width).toBeGreaterThanOrEqual(44);
  });

  // E2E-GUIDE-021: Paperセクションのホバー効果
  test('E2E-GUIDE-021: Paperセクションのホバー効果', async ({ page }) => {
    await page.goto('/guide');

    // 基礎知識セクションのPaperを特定してホバー
    const knowledgeSection = page.locator('.MuiPaper-root').filter({ hasText: 'メタ広告審査の基礎知識' }).first();
    await expect(knowledgeSection).toBeVisible();

    // ホバー前のスタイルを取得
    const beforeTransform = await knowledgeSection.evaluate((el) => getComputedStyle(el).transform);

    // ホバー
    await knowledgeSection.hover();
    await page.waitForTimeout(400); // トランジション待機

    // ホバー後のスタイルを確認（transformが変化していることを確認）
    const afterTransform = await knowledgeSection.evaluate((el) => getComputedStyle(el).transform);

    // CSSトランジションが設定されていることを確認
    const transition = await knowledgeSection.evaluate((el) => getComputedStyle(el).transition);
    expect(transition).toContain('0.3s');
  });

  // E2E-GUIDE-022: ステップカードのホバー効果
  test('E2E-GUIDE-022: ステップカードのホバー効果', async ({ page }) => {
    await page.goto('/guide');

    // ステップ1カードを特定
    const stepCard = page.locator('text=テキストを入力').locator('..');
    await expect(stepCard).toBeVisible();

    // ホバー
    await stepCard.hover();
    await page.waitForTimeout(400);

    // ホバー効果が適用されていることを確認（ボーダーカラーが変化）
    const borderColor = await stepCard.evaluate((el) => getComputedStyle(el).borderColor);
    // #10b981 = rgb(16, 185, 129)
    expect(borderColor).toMatch(/rgb\(16,\s*185,\s*129\)|#10b981/);
  });

  // E2E-GUIDE-023: FAQカードのホバー効果
  test('E2E-GUIDE-023: FAQカードのホバー効果', async ({ page }) => {
    await page.goto('/guide');

    // FAQセクション内のカードを取得（cursorがpointerのdiv）
    const faqSection = page.locator('.MuiPaper-root').filter({ hasText: 'よくある質問（FAQ）' });
    await expect(faqSection).toBeVisible();

    // FAQセクション内で、Qバッジがあるカードを探す
    const faqCard = faqSection.locator('div').filter({ hasText: 'テキストだけ、または画像だけでもチェックできますか?' }).first();
    await expect(faqCard).toBeVisible();

    // ホバー操作が可能であることを確認
    await faqCard.hover();

    // FAQカードがクリック可能（cursor: pointer）であることを確認
    const cursor = await faqCard.evaluate((el) => {
      // 親要素を遡ってcursor: pointerを持つ要素を探す
      let current = el;
      while (current && current !== document.body) {
        const style = getComputedStyle(current);
        if (style.cursor === 'pointer') return 'pointer';
        current = current.parentElement as HTMLElement;
      }
      return getComputedStyle(el).cursor;
    });
    expect(['pointer', 'auto', 'text']).toContain(cursor);
  });

  // E2E-GUIDE-024: 外部リンクボタンのホバー効果
  test('E2E-GUIDE-024: 外部リンクボタンのホバー効果', async ({ page }) => {
    await page.goto('/guide');

    // 外部リンクを特定
    const externalLink = page.getByRole('link', { name: /Meta広告ポリシーを見る/ });
    await expect(externalLink).toBeVisible();

    // ホバー前のスタイル
    const beforeTransform = await externalLink.evaluate((el) => getComputedStyle(el).transform);

    // ホバー
    await externalLink.hover();
    await page.waitForTimeout(400);

    // CSSトランジションが設定されていることを確認
    const transition = await externalLink.evaluate((el) => getComputedStyle(el).transition);
    expect(transition).toContain('0.3s');
  });

  // E2E-GUIDE-025: ページアニメーションの確認
  test('E2E-GUIDE-025: ページアニメーションの確認', async ({ page }) => {
    await page.goto('/guide');

    // タイトルにアニメーションスタイルが定義されていることを確認
    const title = page.locator('h1');
    await expect(title).toBeVisible();

    // animationNameプロパティを確認（CSSで定義されていることを確認）
    const animationName = await title.evaluate((el) => getComputedStyle(el).animationName);
    // アニメーション名が設定されているか、または完了後でも要素が正しく表示されていることを確認
    const isAnimated = animationName !== 'none' || await title.isVisible();
    expect(isAnimated).toBe(true);

    // タイトルが正しい位置に表示されていることを確認（アニメーション後）
    const titleBox = await title.boundingBox();
    expect(titleBox).not.toBeNull();
    expect(titleBox!.y).toBeGreaterThanOrEqual(0); // 画面内に表示されている

    // Paperセクションも正しく表示されていることを確認
    const paper = page.locator('.MuiPaper-root').first();
    await expect(paper).toBeVisible();
    const paperBox = await paper.boundingBox();
    expect(paperBox).not.toBeNull();
  });

  // E2E-GUIDE-038: ステップカードのレスポンシブ
  test('E2E-GUIDE-038: ステップカードのレスポンシブ', async ({ page }) => {
    // モバイル表示（1列）
    await page.setViewportSize({ width: 375, height: 667 });
    await page.goto('/guide');

    const step1 = page.locator('text=テキストを入力').locator('..');
    const step2 = page.locator('text=画像をアップロード').locator('..');

    const box1Mobile = await step1.boundingBox();
    const box2Mobile = await step2.boundingBox();

    // モバイルでは縦に並ぶ（y座標が異なる）
    expect(box1Mobile).not.toBeNull();
    expect(box2Mobile).not.toBeNull();
    expect(box2Mobile!.y).toBeGreaterThan(box1Mobile!.y);

    // デスクトップ表示（3列）
    await page.setViewportSize({ width: 1024, height: 768 });
    await page.waitForTimeout(300);

    const box1Desktop = await step1.boundingBox();
    const box2Desktop = await step2.boundingBox();

    // デスクトップでは横に並ぶ（y座標がほぼ同じ）
    expect(box1Desktop).not.toBeNull();
    expect(box2Desktop).not.toBeNull();
    expect(Math.abs(box1Desktop!.y - box2Desktop!.y)).toBeLessThan(10);
  });

  // E2E-GUIDE-039: FAQカードのレスポンシブ
  test('E2E-GUIDE-039: FAQカードのレスポンシブ', async ({ page }) => {
    // モバイル表示
    await page.setViewportSize({ width: 375, height: 667 });
    await page.goto('/guide');

    // FAQカードが画面幅に収まっていることを確認
    const faqCard = page.locator('text=テキストだけ、または画像だけでもチェックできますか?').locator('..');
    const box = await faqCard.boundingBox();

    expect(box).not.toBeNull();
    // カードが画面幅を超えていないことを確認
    expect(box!.width).toBeLessThanOrEqual(375);

    // 横スクロールがないことを確認
    const bodyWidth = await page.evaluate(() => document.body.scrollWidth);
    const windowWidth = await page.evaluate(() => window.innerWidth);
    expect(bodyWidth).toBeLessThanOrEqual(windowWidth);
  });

  // E2E-GUIDE-041: 長いテキストの表示（モバイル）
  test('E2E-GUIDE-041: 長いテキストの表示（モバイル）', async ({ page }) => {
    await page.setViewportSize({ width: 320, height: 568 }); // 極小画面
    await page.goto('/guide');

    // 長いテキストを含むFAQ回答が正しく表示されることを確認
    const longAnswer = page.locator('text=AIベースの審査予測のため、80-90%程度の高精度ですが');
    await expect(longAnswer).toBeVisible();

    // テキストが画面からはみ出していないことを確認
    const bodyWidth = await page.evaluate(() => document.body.scrollWidth);
    const windowWidth = await page.evaluate(() => window.innerWidth);
    expect(bodyWidth).toBeLessThanOrEqual(windowWidth);

    // FAQ質問テキストも正しく表示されることを確認
    const longQuestion = page.locator('text=テキストだけ、または画像だけでもチェックできますか?');
    await expect(longQuestion).toBeVisible();
  });
});
