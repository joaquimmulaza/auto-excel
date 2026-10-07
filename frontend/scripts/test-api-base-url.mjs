/**
 * Deployment-focused checks for getApiBaseUrl() resolution rules.
 * Mirrors frontend/src/lib/api.ts without a full test runner.
 */
import assert from "node:assert/strict";
import { test } from "node:test";

function getApiBaseUrl({ envUrl } = {}) {
  if (envUrl) {
    return envUrl.replace(/\/$/, "");
  }
  return "http://localhost:8000/api/v1";
}

test("local development defaults to FastAPI on :8000", () => {
  assert.equal(getApiBaseUrl({}), "http://localhost:8000/api/v1");
});

test("without NEXT_PUBLIC_API_URL does not invent same-origin /api/v1", () => {
  assert.equal(
    getApiBaseUrl({}),
    "http://localhost:8000/api/v1"
  );
});

test("NEXT_PUBLIC_API_URL explicit override wins and strips trailing slash", () => {
  assert.equal(
    getApiBaseUrl({
      envUrl: "https://custom.example.com/api/v1/",
    }),
    "https://custom.example.com/api/v1"
  );
});
