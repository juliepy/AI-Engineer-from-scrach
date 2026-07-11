/**
 * Playwright e2e: Book a meeting (schedule page)
 */
import { test, expect } from "@playwright/test";

async function loginAs(page: import("@playwright/test").Page, email: string) {
  await page.goto("/");
  await page.getByPlaceholder("you@company.com").fill(email);
  await page.getByPlaceholder("••••••••").fill("password123");
  await page.getByRole("button", { name: "Sign in" }).click();
  await page.waitForURL("/dashboard");
}

test.describe("Schedule Meeting", () => {
  test("schedule page is accessible from navigation", async ({ page }) => {
    await loginAs(page, "dana@acme.test");
    await page.getByRole("link", { name: "Schedule" }).first().click();
    await expect(page).toHaveURL("/schedule");
    await expect(page.getByText("New Meeting")).toBeVisible();
  });

  test("shows required form fields", async ({ page }) => {
    await loginAs(page, "dana@acme.test");
    await page.goto("/schedule");
    await expect(page.getByLabel("Meeting Title *")).toBeVisible();
    await expect(page.getByLabel("Date *")).toBeVisible();
    await expect(page.getByLabel("Time *")).toBeVisible();
  });

  test("shows validation error when fields missing", async ({ page }) => {
    await loginAs(page, "dana@acme.test");
    await page.goto("/schedule");
    await page.getByRole("button", { name: "Schedule Meeting" }).click();
    await expect(page.getByText(/Title and start date are required/)).toBeVisible();
  });

  test("books a meeting and redirects to detail page", async ({ page }) => {
    await loginAs(page, "dana@acme.test");
    await page.goto("/schedule");
    await page.getByLabel("Meeting Title *").fill("E2E Test Meeting");
    await page.getByLabel("Date *").fill("2026-12-01");
    await page.getByLabel("Time *").fill("10:00");
    await page.getByRole("button", { name: "Schedule Meeting" }).click();
    await expect(page).toHaveURL(/\/meetings\/\d+/);
    await expect(page.getByText("E2E Test Meeting")).toBeVisible();
  });
});
