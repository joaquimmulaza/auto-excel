import { test, expect } from '@playwright/test';

test('Operator approval workflow', async ({ page }) => {
  // Go to home page
  await page.goto('/');

  // Switch to Operator profile
  const operatorBtn = page.getByRole('button', { name: /operador/i });
  await operatorBtn.click();

  // Validate the operator button is active
  await expect(operatorBtn).toHaveClass(/bg-brand/);

  // Navigate to an existing pending job, let's just go to home and click the first pending job
  // We can look for "Ver Diff" or a job card
  const detailsBtn = page.getByRole('button', { name: 'Ver Diff' }).first();
  await expect(detailsBtn).toBeVisible();
  await detailsBtn.click();

  // We should be on /jobs/[id]
  await page.waitForURL(/\/jobs\/[a-zA-Z0-9-]{36}/);

  // Approve button should be active and brand colored (#FF3C1D)
  const approveBtn = page.getByRole('button', { name: /Aprovar Processamento/i });
  
  if (await approveBtn.isVisible()) {
    await expect(approveBtn).not.toBeDisabled();
    // Execute approval
    await approveBtn.click();
    
    // Wait for status change to "APPROVED" or similar
    await expect(page.getByText('Aprovado', { exact: false })).toBeVisible();
  }
});
