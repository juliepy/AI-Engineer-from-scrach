/**
 * Unit tests for the API client utility functions.
 */
import { describe, it, expect, beforeEach, vi } from "vitest";
import { getToken, setToken, clearToken, exportUrl } from "@/lib/api";

// Provide localStorage mock for jsdom
beforeEach(() => {
  localStorage.clear();
  vi.restoreAllMocks();
});

describe("Token utilities", () => {
  it("getToken returns null when no token stored", () => {
    expect(getToken()).toBeNull();
  });

  it("setToken stores the token", () => {
    setToken("my-token");
    expect(localStorage.getItem("schedulr_token")).toBe("my-token");
  });

  it("getToken returns the stored token", () => {
    localStorage.setItem("schedulr_token", "abc123");
    expect(getToken()).toBe("abc123");
  });

  it("clearToken removes the token", () => {
    localStorage.setItem("schedulr_token", "abc123");
    clearToken();
    expect(getToken()).toBeNull();
  });
});

describe("exportUrl", () => {
  it("returns a URL containing the format", () => {
    const url = exportUrl("pdf");
    expect(url).toContain("format=pdf");
    expect(url).toContain("/api/meetings/export");
  });
});
