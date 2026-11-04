// Simulator confirmation of the lessons' tryIt items (pending-ci).
// Each test flashes main.py with the same variant used by the lab's try_it.py
// (labs/L100/<lab>/try_it.json) and checks the serial output.
// Not covered here: 01 no-guard (on the board main.py is always __main__) and
// 04 tune length (stub/model only; timing is not asserted).
const { test, expect } = require("@playwright/test");
const { openSimulator, flash, flashCode, variantCode, setValue, click, waitForSerial } = require("./sim-helpers");

const NL = String.raw`\r?\n`;

test.beforeEach(async ({ page }) => {
  await openSimulator(page);
});

test("tryIt 01 fast-tick: 4 ticks within ~1 s", async ({ page }) => {
  await flashCode(page, variantCode("01-setup", "fast-tick"));
  await waitForSerial(page, /hello from micro:bit/);
  await waitForSerial(page, /tick 4/, 2_500);   // sleep(1000) would need ~4 s
});

test("tryIt 02 ramp-mod5: brightness wraps after 4", async ({ page }) => {
  await flashCode(page, variantCode("02-led-display", "ramp-mod5"));
  await waitForSerial(page, new RegExp(`brightness 4${NL}brightness 0`));
});

test("tryIt 03 count-with-was-pressed: quick clicks in a slow loop count once", async ({ page }) => {
  await flashCode(page, variantCode("03-buttons", "count-with-was-pressed"));
  await waitForSerial(page, /A = \+1, B = reset/);
  for (let i = 0; i < 3; i++) await click(page, "buttonA", 60);
  await waitForSerial(page, /count 1/, 8_000);
  await page.waitForTimeout(3_500);
  expect(await page.evaluate(() => window.sim.serial)).not.toMatch(/count 3/);
});

test("tryIt 03 count-with-is-pressed: holding A keeps counting", async ({ page }) => {
  await flashCode(page, variantCode("03-buttons", "count-with-is-pressed"));
  await waitForSerial(page, /A = \+1, B = reset/);
  await setValue(page, "buttonA", 1);
  await waitForSerial(page, /count 3/);
  await setValue(page, "buttonA", 0);
});

test("tryIt 04 speaker off: tune still played", async ({ page }) => {
  await flash(page, "04-sound");   // prediction only, no code change
  await waitForSerial(page, /sound ready/);
  await click(page, "buttonB");
  await click(page, "buttonA");
  await waitForSerial(page, new RegExp(`speaker off${NL}tune played`));
});

test("tryIt 05 hot-28: 27 C is ok", async ({ page }) => {
  await flashCode(page, variantCode("05-temperature-light", "hot-28"));
  await waitForSerial(page, /temp=/);
  await setValue(page, "lightLevel", 128);
  await setValue(page, "temperature", 27);
  await waitForSerial(page, /temp=27,light=128,state=ok/);
});

test("tryIt 05 hot-first: hot wins over dark", async ({ page }) => {
  await flashCode(page, variantCode("05-temperature-light", "hot-first"));
  await waitForSerial(page, /temp=/);
  await setValue(page, "lightLevel", 10);
  await setValue(page, "temperature", 30);
  await waitForSerial(page, /temp=30,light=10,state=hot/);
});

test("tryIt 06 tilt-100: x=200 is right", async ({ page }) => {
  await flashCode(page, variantCode("06-motion-gestures", "tilt-100"));
  await waitForSerial(page, /tilt=/);
  await setValue(page, "accelerometerX", 200);
  await waitForSerial(page, /x=200,.*tilt=right/);
});

test("tryIt 06 is-gesture: one shake reported repeatedly", async ({ page }) => {
  await flashCode(page, variantCode("06-motion-gestures", "is-gesture"));
  await waitForSerial(page, /tilt=/);
  await setValue(page, "gesture", "shake");
  await waitForSerial(page, /shake![\s\S]*shake!/);
  await setValue(page, "gesture", "none");
});
