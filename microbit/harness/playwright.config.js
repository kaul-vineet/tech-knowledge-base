// @ts-check
const { defineConfig, devices } = require("@playwright/test");

const PORT = Number(process.env.PORT || 4173);

module.exports = defineConfig({
  testDir: ".",
  testMatch: /(simulator|tryit)(-l200|-l300)?\.spec\.js$/,
  timeout: 120_000,            // simulator (WASM) download + boot can be slow
  expect: { timeout: 20_000 },
  retries: process.env.CI ? 1 : 0,
  workers: 1,                  // one simulator at a time keeps timing predictable
  reporter: [["list"]],
  use: {
    baseURL: `http://127.0.0.1:${PORT}`,  // explicit IPv4: same on macOS, Windows, Linux
    trace: "retain-on-failure",
  },
  projects: [{ name: "chromium", use: { ...devices["Desktop Chrome"] } }],
  webServer: {
    command: "node serve.js",
    url: `http://127.0.0.1:${PORT}/`,
    reuseExistingServer: !process.env.CI,
    env: { PORT: String(PORT) },
  },
});
