import { Page } from '@playwright/test';

export async function navigateToHome(page: Page) {
  await page.goto('/');
  await page.waitForLoadState('networkidle');
}

export async function navigateToGuide(page: Page) {
  await page.goto('/guide');
  await page.waitForLoadState('networkidle');
}

export async function clickGuideLinkInHeader(page: Page) {
  await page.getByRole('button', { name: '使い方ガイド' }).click();
  await page.waitForURL('/guide');
}

export async function clickLogoToReturnHome(page: Page) {
  await page.getByText('メタ広告審査チェッカー').first().click();
  await page.waitForURL('/');
}
