/**
 * Playwright e2e: Login flow
 */
import { test, expect } from "@playwright/test";

test.describe("Login", () => {
  test("shows login form on root route", async ({ page }) => {
    await page.goto("/");
    await expect(page.locator("h2")).toContainText("Sign in");
    await expect(page.getByPlaceholder("you@company.com")).toBeVisible();
    await expect(page.getByPlaceholder("••••••••")).toBeVisible();
  });

  test("shows demo users in the hint box", async ({ page }) => {
    await page.goto("/");
    await expect(page.getByText("Dana Ortiz")).toBeVisible();
    await expect(page.getByText("Lukas Berg")).toBeVisible();
    await expect(page.getByText("Mei Tan")).toBeVisible();
  });

  test("logs in with valid credentials and redirects to dashboard", async ({ page }) => {
    await page.goto("/");
    await page.getByPlaceholder("you@company.com").fill("dana@acme.test");
    await page.getByPlaceholder("••••••••").fill("password123");
    await page.getByRole("button", { name: "Sign in" }).click();
    await expect(page).toHaveURL("/dashboard");
  });

  test("shows error message with wrong credentials", async ({ page }) => {
    await page.goto("/");
    await page.getByPlaceholder("you@company.com").fill("wrong@acme.test");
    await page.getByPlaceholder("••••••••").fill("wrongpass");
    await page.getByRole("button", { name: "Sign in" }).click();
    await expect(page.getByText(/Invalid email or password/)).toBeVisible();
  });

  test("demo user buttons fill the form", async ({ page }) => {
    await page.goto("/");
    await page.getByText("Lukas Berg").click();
    await expect(page.getByPlaceholder("you@company.com")).toHaveValue("lukas@acme.test");
  });
});
