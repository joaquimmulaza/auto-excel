import { test, expect } from "@playwright/test";

async function loginAs(page: import("@playwright/test").Page, role: "comercial" | "operador") {
  await page.goto("/login");
  if (role === "operador") {
    await page.getByRole("button", { name: "Operador" }).click();
  } else {
    await page.getByRole("button", { name: "Comercial" }).click();
  }
  await page.getByRole("button", { name: "Entrar" }).click();
  await page.waitForURL("/");
}

test("Operator approval workflow UI", async ({ page }) => {
  await loginAs(page, "operador");
  await expect(page.getByText(/Olá,/i)).toBeVisible();
  await expect(page.getByText("OPERADOR")).toBeVisible();
});
