/**
 * Deployment-focused checks for getApiBaseUrl() resolution rules.
 * Mirrors frontend/src/lib/api.ts without a full test runner.
 */
import assert from "node:assert/strict";
import { test } from "node:test";

function getApiBaseUrl({ envUrl, hostname, origin } = {}) {
  if (envUrl) {
    return envUrl.replace(/\/$/, "");
  }
  if (hostname && hostname !== "localhost" && hostname !== "127.0.0.1") {
    return `${origin}/api/v1`;
  }
  return "http://localhost:8000/api/v1";
}

test("local development defaults to FastAPI on :8000", () => {
  assert.equal(
    getApiBaseUrl({ hostname: "localhost", origin: "http://localhost:3000" }),
    "http://localhost:8000/api/v1"
  );
  assert.equal(
    getApiBaseUrl({ hostname: "127.0.0.1", origin: "http://127.0.0.1:3000" }),
    "http://localhost:8000/api/v1"
  );
});

test("production / non-localhost uses same-origin /api/v1", () => {
  assert.equal(
    getApiBaseUrl({
      hostname: "auto-excel.vercel.app",
      origin: "https://auto-excel.vercel.app",
    }),
    "https://auto-excel.vercel.app/api/v1"
  );
});

test("NEXT_PUBLIC_API_URL explicit override wins and strips trailing slash", () => {
  assert.equal(
    getApiBaseUrl({
      envUrl: "https://custom.example.com/api/v1/",
      hostname: "auto-excel.vercel.app",
      origin: "https://auto-excel.vercel.app",
    }),
    "https://custom.example.com/api/v1"
  );
});
