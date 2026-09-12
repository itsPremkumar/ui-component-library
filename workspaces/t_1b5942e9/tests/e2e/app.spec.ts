import { test, expect } from '@playwright/test';

test.describe('Test Results Visualizer', () => {
  test.beforeEach(async ({ page }) => {
    await page.goto('/');
  });

  test('displays the dashboard with sample data', async ({ page }) => {
    await expect(page.locator('text=Dashboard')).toBeVisible();
    // Sample data loads automatically
    await expect(page.locator('text=Total Tests')).toBeVisible({ timeout: 10000 });
  });

  test('navigates to test cases view', async ({ page }) => {
    await page.click('text=Test Cases');
    await expect(page.locator('text=Search test names...')).toBeVisible();
  });

  test('navigates to upload view', async ({ page }) => {
    await page.click('text=Upload');
    await expect(page.locator('text=Drop test report files here')).toBeVisible();
  });

  test('navigates to compare view', async ({ page }) => {
    await page.click('text=Compare');
    await expect(page.locator('text=Load Sample Data')).toBeVisible();
  });

  test('loads sample data from empty state', async ({ page }) => {
    // Navigate to compare which shows empty state
    await page.click('text=Compare');
    await page.click('text=Load Sample Data');
    await expect(page.locator('text=Pass Rate Change')).toBeVisible({ timeout: 10000 });
  });

  test('displays summary cards with correct data', async ({ page }) => {
    await expect(page.locator('text=Total Tests')).toBeVisible({ timeout: 10000 });
    await expect(page.locator('text=Pass Rate')).toBeVisible();
    await expect(page.locator('text=Passed')).toBeVisible();
    await expect(page.locator('text=Failed')).toBeVisible();
  });

  test('shows suite breakdown chart', async ({ page }) => {
    await expect(page.locator('text=Suite Breakdown')).toBeVisible({ timeout: 10000 });
  });

  test('shows duration histogram', async ({ page }) => {
    await expect(page.locator('text=Duration Distribution')).toBeVisible({ timeout: 10000 });
  });

  test('filters tests by status', async ({ page }) => {
    await page.click('text=Test Cases');
    await page.click('text=passed');
    // Should filter the table
    await expect(page.locator('text=Showing')).toBeVisible();
  });

  test('searches tests by name', async ({ page }) => {
    await page.click('text=Test Cases');
    await page.fill('input[placeholder="Search test names..."]', 'login');
    await expect(page.locator('text=Showing')).toBeVisible();
  });
});
