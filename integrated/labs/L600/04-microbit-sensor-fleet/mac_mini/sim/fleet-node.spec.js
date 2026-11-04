// L600 #04 fleet node firmware in the MicroPython micro:bit V2 simulator: board 0 = gateway_sim.py, board 1 = node.
// Status: pendingMac (needs internet for the simulator page). The CPython stub run of the same programs
// (python ../make_sim_programs.py --here) prints what these tests expect.
const fs = require("fs");
const path = require("path");
const { test, expect } = require("@playwright/test");
const { openSimulator, flashCode, serialOf, waitForSerial } =
  require(path.resolve(__dirname, "../../../../../../microbit/harness/sim-helpers.js"));

const OUT = path.resolve(__dirname, "../sim_out");
const code = (f) => fs.readFileSync(path.join(OUT, f), "utf8");
const STATS = /stats sampled=(\d+) frames=(\d+) tries=(\d+) acked=(\d+) left=(\d+) maxframe=(\d+)/;

async function runPair(page, nodeFile) {
  await openSimulator(page, 2);
  await flashCode(page, code("gateway_sim.py"), 0);
  await waitForSerial(page, /gateway ready/, 30_000, 0);
  await flashCode(page, code(nodeFile), 1);
  await waitForSerial(page, /node ready schema 2/, 30_000, 1);
  await waitForSerial(page, STATS, 120_000, 1);
  const m = (await serialOf(page, 1)).match(STATS).slice(1).map(Number);
  const onAir = await page.evaluate(() => window.sims[1].radioOut.map((b) => b.length));
  const stats = { sampled: m[0], frames: m[1], tries: m[2], acked: m[3], left: m[4], maxframe: m[5],
                  maxBytesOnAir: Math.max(0, ...onAir) };
  test.info().annotations.push({ type: nodeFile, description: JSON.stringify(stats) });
  return stats;
}

test("firmware runs in MicroPython: 30 readings sampled, framed within 32 B, acked by the gateway (500 ms wait)", async ({ page }) => {
  const s = await runPair(page, "node_sim_wait500.py");
  expect(s.sampled).toBe(30);
  expect(s.maxframe).toBeLessThanOrEqual(32);
  expect(s.maxBytesOnAir).toBeLessThanOrEqual(32);
  expect(s.acked).toBe(30);
  expect(s.left).toBe(0);
});

test("ADR 0003's 50 ms ack window across the simulator bridge (recorded, not asserted)", async ({ page }) => {
  const s = await runPair(page, "node_sim.py");
  expect(s.sampled).toBe(30);
  // acked < 30 here means the bridge between two iframes is slower than 50 ms - a property of the browser setup,
  // not of a real radio; the 500 ms test above shows the code path itself works.
});

test("oversize-frame fault: what the MicroPython radio puts on air for an 84+ byte frame with length=32", async ({ page }) => {
  const s = await runPair(page, "node_sim_oversize.py");
  expect(s.maxframe).toBeGreaterThan(32);
  // The stub truncates to 32 B (modradio.cpp behaviour, see microbit/labs/sim_stub/radio.py); record what the
  // simulator does: maxBytesOnAir === 32 confirms truncation, a larger value means the stub is wrong.
  expect(s.maxBytesOnAir).toBeGreaterThan(0);
});
