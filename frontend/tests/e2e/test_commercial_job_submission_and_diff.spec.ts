import { test, expect } from "@playwright/test";
import path from "path";

test("Commercial job submission with fixture upload", async ({ page }) => {
  await page.goto("/login");
  await page.getByRole("button", { name: "Comercial" }).click();
  await page.getByRole("button", { name: "Entrar" }).click();
  await page.waitForURL("/");

  await page.goto("/jobs/new");
  await expect(page.getByText("Novo Processamento")).toBeVisible();

  const fixture = path.join(
    __dirname,
    "../../../fixtures/excel/sample_input_samsung.xlsx"
  );
  const catalog = path.join(
    __dirname,
    "../../../fixtures/excel/sample_catalog.xlsx"
  );

  // First upload zone = INPUT; second = CATALOG
  const fileInputs = page.locator('input[type="file"]');
  await fileInputs.nth(0).setInputFiles(fixture);
  await fileInputs.nth(1).setInputFiles(catalog);

  await page.getByRole("button", { name: /Validar Ficheiro/i }).click();
  await page.waitForURL(/\/jobs\/[a-zA-Z0-9-]{36}/, { timeout: 60000 });
  await expect(page.getByText(/Diferencial de Preços/i)).toBeVisible({
    timeout: 30000,
  });
});
