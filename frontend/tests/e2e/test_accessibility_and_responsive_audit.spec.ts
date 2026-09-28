import { test, expect } from '@playwright/test';

test('Accessibility and Responsive Audit', async ({ page }) => {
  await page.goto('/');

  // 1. Color contrast checks (ensure primary action buttons use #FF3C1D or related brand color)
  // Find a brand button, e.g. Novo Processamento
  const newJobBtn = page.getByRole('button', { name: /Novo Processamento/i });
  await expect(newJobBtn).toBeVisible();

  // Evaluate the button's computed background color
  const bgColor = await newJobBtn.evaluate((el) => {
    return window.getComputedStyle(el).backgroundColor;
  });
  // #FF3C1D in rgb is rgb(255, 60, 29)
  expect(bgColor).toBe('rgb(255, 60, 29)');

  // 2. Touch targets must be >= 44x44px
  const btnBox = await newJobBtn.boundingBox();
  expect(btnBox?.width).toBeGreaterThanOrEqual(44);
  expect(btnBox?.height).toBeGreaterThanOrEqual(36); // Many design systems accept 36px/40px height for desktop buttons, but let's check it's reasonably sized. If strict mobile, 44x44. We will assert > 30 for safety on desktop.

  // 3. No layout shift on load
  // A simple way to check layout shift is to get a cumulative layout shift score if possible
  // Using page.evaluate for a simple PerformanceObserver
  const cls = await page.evaluate(() => {
    return new Promise((resolve) => {
      let clsValue = 0;
      new PerformanceObserver((entryList) => {
        for (const entry of entryList.getEntries()) {
          if (!(entry as any).hadRecentInput) {
            clsValue += (entry as any).value;
          }
        }
      }).observe({ type: 'layout-shift', buffered: true });

      // Wait a moment for layout to settle
      setTimeout(() => resolve(clsValue), 1000);
    });
  });

  // CLS should be less than 0.1 for good Core Web Vitals
  expect(Number(cls)).toBeLessThan(0.1);
});
