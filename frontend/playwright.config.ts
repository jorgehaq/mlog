import { defineConfig, devices } from '@playwright/test'

const useExternal = !!process.env.E2E_BASE_URL;

export default defineConfig({
  testDir: './e2e',
  fullyParallel: true,
  reporter: 'list',
  use: {
    baseURL: process.env.E2E_BASE_URL || 'http://localhost:4173',
    trace: 'on-first-retry',
  },
  webServer: useExternal
    ? undefined
    : {
        command: 'sh -lc "npm run build && npm run preview -- --port 4173 --host 0.0.0.0"',
        url: 'http://localhost:4173',
        timeout: 180_000,
        reuseExistingServer: !process.env.CI,
      },
  projects: [
    { name: 'chromium', use: { ...devices['Desktop Chrome'] } },
  ],
})
