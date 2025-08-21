import { defineConfig } from '@playwright/test';

export default defineConfig({
  testDir: 'apps/web/tests',
  use: { baseURL: 'http://localhost:3000' },
  webServer: {
    command: 'npm run dev --prefix apps/web',
    port: 3000,
    reuseExistingServer: !process.env.CI,
  },
});
