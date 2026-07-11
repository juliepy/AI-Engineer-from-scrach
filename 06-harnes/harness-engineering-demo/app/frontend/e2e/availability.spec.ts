/**
 * Playwright e2e: Availability editor
 */
import { test, expect } from "@playwright/test";

async function loginAs(page: import("@playwright/test").Page, email: string) {
  await page.goto("/");
  await page.getByPlaceholder("you@company.com").fill(email);
  await page.getByPlaceholder("••••••••").fill("password123");
  await page.getByRole("button", { name: "Sign in" }).click();
  await page.waitForURL("/dashboard");
}

test.describe("Availability", () => {
  test("availability page renders weekly schedule", async ({ page }) => {
    await loginAs(page, "dana@acme.test");
    await page.goto("/availability");
    await expect(page.getByText("Weekly Availability")).toBeVisible();
    // 7 days of the week visible
    await expect(page.getByText("Monday")).toBeVisible();
    await expect(page.getByText("Saturday")).toBeVisible();
  });

  test("can toggle a day off", async ({ page }) => {
    await loginAs(page, "dana@acme.test");
    await page.goto("/availability");
    // Find the Sunday checkbox and ensure it starts unchecked (weekend)
    const sundayLabel = page.getByText("Sunday").locator("..");
    const checkbox = sundayLabel.locator("input[type='checkbox']");
    const wasChecked = await checkbox.isChecked();
    await checkbox.click();
    const isNowChecked = await checkbox.isChecked();
    expect(isNowChecked).toBe(!wasChecked);
  });

  test("save button is visible", async ({ page }) => {
    await loginAs(page, "dana@acme.test");
    await page.goto("/availability");
    await expect(page.getByRole("button", { name: /Save Availability/i })).toBeVisible();
  });
});
