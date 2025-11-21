import { expect, test } from "@playwright/test";

test.describe("Homepage", () => {
  test("should display the main heading", async ({ page }) => {
    await page.goto("/");

    await expect(page.getByRole("heading", { name: /AICA-SyS/i })).toBeVisible();
  });

  test("should navigate to pricing page", async ({ page }) => {
    await page.goto("/");

    await page.getByRole("link", { name: /料金/i }).click();
    await expect(page).toHaveURL("/pricing");
  });

  test("should navigate to articles page", async ({ page }) => {
    await page.goto("/");

    await page.getByRole("link", { name: /記事/i }).click();
    await expect(page).toHaveURL("/articles");
  });

  test("should navigate to newsletters page", async ({ page }) => {
    await page.goto("/");

    await page.getByRole("link", { name: /ニュースレター/i }).click();
    await expect(page).toHaveURL("/newsletters");
  });

  test("should navigate to trends page", async ({ page }) => {
    await page.goto("/");

    await page.getByRole("link", { name: /トレンド/i }).click();
    await expect(page).toHaveURL("/trends");
  });
});
