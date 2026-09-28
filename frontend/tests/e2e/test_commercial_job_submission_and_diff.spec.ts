import { test, expect } from '@playwright/test';
import path from 'path';

test('Commercial job submission and diff viewer validation', async ({ page }) => {
  // Go to home page
  await page.goto('/');

  // Switch to Comercial profile
  const comercialBtn = page.getByRole('button', { name: /comercial/i });
  await comercialBtn.click();

  // Verify switched to Comercial
  await expect(comercialBtn).toHaveClass(/bg-surface/);

  // Navigate to new job
  await page.getByRole('button', { name: /Novo Processamento/i }).click();
  await page.waitForURL('/jobs/new');

  // We should be on /jobs/new. The Select for Profile is likely default "Marketplace Mano"
  const selectLocator = page.locator('select').first();
  // Ensure "Marketplace Mano" is selected or select it
  // Since we don't have the exact option value, we can select by label
  await selectLocator.selectOption({ label: 'Marketplace Mano (MARKETPLACE)' });

  // Upload file
  const fileInput = page.locator('input[type="file"]');
  const testFile = 'C:\\up_prices\\Mano-preco-desatualizado.xlsx';
  await fileInput.setInputFiles(testFile);

  // Submit form
  await page.getByRole('button', { name: /Validar Ficheiro/i }).click();

  // Should redirect to /jobs/[id]
  await page.waitForURL(/\/jobs\/.+/);

  // Validate the DiffViewer is visible by checking for a table header or "Todos" button
  await expect(page.getByRole('button', { name: /Todos/i }).first()).toBeVisible();

  // Filters in DiffViewer
  const filterTodos = page.getByRole('button', { name: /Todos/i });
  const filterAtualizados = page.getByRole('button', { name: /Atualiza/i });
  const filterBloqueados = page.getByRole('button', { name: /Bloqueados/i });

  await expect(filterTodos).toBeVisible();
  await filterAtualizados.click();
  await filterBloqueados.click();

  // Test AI anomaly explanation if there's a blocker
  // Click on "Explicar com IA" if visible
  const explainBtn = page.getByRole('button', { name: /Explicar/i }).first();
  if (await explainBtn.isVisible()) {
    await explainBtn.click();
    // Validate modal opens
    await expect(page.getByText('Diagnóstico Assistivo Gemini', { exact: false })).toBeVisible();
    await page.getByRole('button', { name: /Fechar/i }).first().click();
  }

  // Validate "Aprovar Processamento" is disabled for Comercial or warns
  const approveBtn = page.getByRole('button', { name: /Aprovar Processamento/i });
  if (await approveBtn.isVisible()) {
    await expect(approveBtn).toBeDisabled();
  }
});
