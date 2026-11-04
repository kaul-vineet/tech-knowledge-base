// @ts-check
// L600 #04 on the real simulator. Reuses the microbit topic's harness (host page, loopback server, helpers): nothing
// is copied; the topic's files are referenced by path. Run `python ../make_sim_programs.py` first (writes ../sim_out).
const path = require("path");
const { defineConfig, devices } = require("@playwright/test");

const PORT = Number(process.env.PORT || 4174);
const HARNESS = path.resolve(__dirname, "../../../../../../microbit/harness");

module.exports = defineConfig({
  testDir: ".",
  testMatch: /fleet-node\.spec\.js$/,
  timeout: 180_000,
  expect: { timeout: 30_000 },
  workers: 1,
  reporter: [["list"], ["json", { outputFile: "../runs/playwright-report.json" }]],
  use: { baseURL: `http://127.0.0.1:${PORT}`, trace: "retain-on-failure" },
  projects: [{ name: "chromium", use: { ...devices["Desktop Chrome"] } }],
  webServer: {
    command: `node "${path.join(HARNESS, "serve.js")}"`,
    url: `http://127.0.0.1:${PORT}/`,
    reuseExistingServer: !process.env.CI,
    env: { PORT: String(PORT) },
  },
});
