import { test, expect } from '@playwright/test'

test.describe('Pricing Page', () => {
  test('should display all pricing plans', async ({ page }) => {
    await page.goto('/pricing')
    
    await expect(page.getByText('フリープラン')).toBeVisible()
    await expect(page.getByText('プレミアムプラン')).toBeVisible()
    await expect(page.getByText('エンタープライズプラン')).toBeVisible()
  })

  test('should display correct pricing', async ({ page }) => {
    await page.goto('/pricing')
    
    await expect(page.getByText('¥0/月')).toBeVisible()
    await expect(page.getByText('¥1,980/月')).toBeVisible()
    await expect(page.getByText('¥9,800/月')).toBeVisible()
  })

  test('should show popular badge on premium plan', async ({ page }) => {
    await page.goto('/pricing')
    
    await expect(page.getByText('人気')).toBeVisible()
  })

  test('should display plan features', async ({ page }) => {
    await page.goto('/pricing')
    
    await expect(page.getByText('基本記事閲覧')).toBeVisible()
    await expect(page.getByText('全記事閲覧')).toBeVisible()
    await expect(page.getByText('無制限アクセス')).toBeVisible()
  })

  test('should have subscribe buttons', async ({ page }) => {
    await page.goto('/pricing')
    
    const subscribeButtons = page.getByRole('button', { name: /今すぐ始める/i })
    await expect(subscribeButtons).toHaveCount(3)
  })
})
