import { test, expect } from '@playwright/test';
import path from 'path';

const fixture = path.join(__dirname, 'fixtures', 'resume.pdf');

// Mock API responses to avoid network calls
async function mockApis(page) {
  await page.route('**/v1/parse/resume', route => {
    route.fulfill({ status: 200, contentType: 'application/json', body: JSON.stringify({ doc_id: 'r1' }) });
  });
  await page.route('**/v1/parse/job', route => {
    route.fulfill({ status: 200, contentType: 'application/json', body: JSON.stringify({ doc_id: 'j1' }) });
  });
  await page.route('**/v1/match', route => {
    route.fulfill({ status: 200, contentType: 'application/json', body: JSON.stringify({ score: 92, label: 'Great' }) });
  });
}

test('uploads resume and job and shows match label', async ({ page }) => {
  await mockApis(page);
  await page.goto('/');
  await page.setInputFiles('input[type=file]', fixture);
  await page.fill('textarea', 'Example job description');
  await page.click('text=Analyze');
  await expect(page).toHaveURL(/result/);
  await expect(page.locator('text=Great')).toBeVisible();
});
