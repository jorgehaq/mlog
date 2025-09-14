import { test, expect } from '@playwright/test'

test('homepage renders and navigates', async ({ page }) => {
  await page.goto('/')
  await expect(page.getByRole('heading', { name: /mlog/ })).toBeVisible()
  await page.getByRole('button', { name: 'Dashboard' }).click()
  await expect(page.getByRole('heading', { name: 'Dashboard' })).toBeVisible()
  await page.getByRole('button', { name: 'Crear evento' }).click()
  await expect(page.getByRole('heading', { name: 'Crear evento' })).toBeVisible()
})

