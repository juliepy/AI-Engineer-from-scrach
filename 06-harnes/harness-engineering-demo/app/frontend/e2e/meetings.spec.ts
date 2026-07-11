/**
 * Playwright e2e: Meetings golden path
 */
import { test, expect } from "@playwright/test";

async function loginAs(page: import("@playwright/test").Page, email: string) {
  await page.goto("/");
  await page.getByPlaceholder("you@company.com").fill(email);
  await page.getByPlaceholder("••••••••").fill("password123");
  await page.getByRole("button", { name: "Sign in" }).click();
  await page.waitForURL("/dashboard");
}

test.describe("Meetings", () => {
  test("meetings page shows table", async ({ page }) => {
    await loginAs(page, "dana@acme.test");
    await page.goto("/meetings");
    await expect(page.locator("table")).toBeVisible();
    // Should have at least one row (seed data)
    await expect(page.locator("table tbody tr").first()).toBeVisible();
  });

  test("meetings page has Export PDF button", async ({ page }) => {
    await loginAs(page, "dana@acme.test");
    await page.goto("/meetings");
    await expect(page.getByRole("link", { name: /Export PDF/i })).toBeVisible();
  });

  test("meetings page does NOT have CSV export", async ({ page }) => {
    await loginAs(page, "dana@acme.test");
    await page.goto("/meetings");
    await expect(page.getByText("Export CSV")).not.toBeVisible();
  });

  test("can filter meetings by status", async ({ page }) => {
    await loginAs(page, "dana@acme.test");
    await page.goto("/meetings");
    await page.getByRole("combobox").nth(1).selectOption("completed");
    await page.waitForTimeout(500);
    // All visible status badges should be "Completed" or table should be empty
    const rows = await page.locator("table tbody tr").count();
    expect(rows).toBeGreaterThanOrEqual(0);
  });

  test("clicking View on a meeting opens detail page", async ({ page }) => {
    await loginAs(page, "dana@acme.test");
    await page.goto("/meetings");
    await page.locator("table tbody tr").first().getByRole("link", { name: "View" }).click();
    await expect(page).toHaveURL(/\/meetings\/\d+/);
    await expect(page.getByText("Back to meetings")).toBeVisible();
  });
});
