import { defineConfig, devices } from '@playwright/test';

export default defineConfig({
  testDir: './e2e',
  outputDir: './test-results',

  fullyParallel: true,
  forbidOnly: !!process.env.CI,
  retries: process.env.CI ? 2 : 0,
  workers: process.env.CI ? 1 : undefined,

  timeout: 60000,

  reporter: [
    ['html', { outputFolder: './playwright-report', open: 'never' }],
    ['list']
  ],

  use: {
    baseURL: 'http://localhost:3247',
    headless: true,
    trace: 'retain-on-failure',
    screenshot: {
      mode: 'only-on-failure',
      fullPage: true,
    },
    video: 'retain-on-failure',
  },

  projects: [
    {
      name: 'chromium',
      use: { ...devices['Desktop Chrome'] },
    },
  ],

  webServer: {
    command: 'cd frontend && npm run dev',
    url: 'http://localhost:3247',
    reuseExistingServer: !process.env.CI,
    timeout: 120000,
  },
});
