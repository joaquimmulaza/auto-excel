import { test, expect } from "@playwright/test";

test("Accessibility and Responsive Audit", async ({ page }) => {
  await page.goto("/login");
  await page.getByRole("button", { name: "Comercial" }).click();
  await page.getByRole("button", { name: "Entrar" }).click();
  await page.waitForURL("/");

  const newJobBtn = page.getByRole("button", { name: /Novo Processamento/i }).first();
  await expect(newJobBtn).toBeVisible();

  const bgColor = await newJobBtn.evaluate((el) => {
    return window.getComputedStyle(el).backgroundColor;
  });
  expect(bgColor).toBe("rgb(255, 60, 29)");

  const btnBox = await newJobBtn.boundingBox();
  expect(btnBox?.width).toBeGreaterThanOrEqual(44);
  expect(btnBox?.height).toBeGreaterThanOrEqual(30);

  const cls = await page.evaluate(() => {
    return new Promise((resolve) => {
      let clsValue = 0;
      new PerformanceObserver((entryList) => {
        for (const entry of entryList.getEntries()) {
          if (!(entry as { hadRecentInput?: boolean }).hadRecentInput) {
            clsValue += (entry as { value: number }).value;
          }
        }
      }).observe({ type: "layout-shift", buffered: true });
      setTimeout(() => resolve(clsValue), 1000);
    });
  });
  expect(cls).toBeLessThan(0.25);
});
