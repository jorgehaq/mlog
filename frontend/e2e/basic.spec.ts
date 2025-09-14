import { test, expect } from '@playwright/test'

test('homepage renders and navigates', async ({ page }) => {
  await page.goto('/')
  await expect(page.getByText('mlog')).toBeVisible()
  await page.getByRole('button', { name: 'Dashboard' }).click()
  await expect(page.getByText('Dashboard')).toBeVisible()
  await page.getByRole('button', { name: 'Crear evento' }).click()
  await expect(page.getByText('Crear evento')).toBeVisible()
})

