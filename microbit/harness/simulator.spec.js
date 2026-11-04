// End-to-end checks: each L100 lab runs in the real MicroPython simulator.
// Requires internet (loads python-simulator.usermbit.org). Run in CI.
const { test, expect } = require("@playwright/test");
const { openSimulator, flash, setValue, click, waitForSerial } = require("./sim-helpers");

test.beforeEach(async ({ page }) => {
  await openSimulator(page);
});

test("01-setup prints hello and ticks", async ({ page }) => {
  await flash(page, "01-setup");
  await waitForSerial(page, /hello from micro:bit/);
  await waitForSerial(page, /tick 2/);
});

test("02-led-display runs intro then brightness ramp", async ({ page }) => {
  await flash(page, "02-led-display");
  await waitForSerial(page, /intro done/);
  await waitForSerial(page, /brightness 9/);
});

test("03-buttons counts A presses and resets with B", async ({ page }) => {
  await flash(page, "03-buttons");
  await waitForSerial(page, /A = \+1, B = reset/);
  for (let i = 0; i < 3; i++) await click(page, "buttonA");
  await waitForSerial(page, /count 3/);
  await click(page, "buttonB");
  await waitForSerial(page, /count 0/);
});

test("04-sound reacts to A, B and logo", async ({ page }) => {
  await flash(page, "04-sound");
  await waitForSerial(page, /sound ready/);
  await click(page, "buttonB");
  await waitForSerial(page, /speaker off/);
  await click(page, "buttonA");
  await waitForSerial(page, /tune played/);
  await click(page, "pinLogo");
  await waitForSerial(page, /effect played/);
});

test("05-temperature-light follows injected sensor values", async ({ page }) => {
  await flash(page, "05-temperature-light");
  await waitForSerial(page, /temp=/);
  await setValue(page, "lightLevel", 200);
  await setValue(page, "temperature", 30);
  await waitForSerial(page, /temp=30,light=200,state=hot/);
  await setValue(page, "lightLevel", 10);
  await waitForSerial(page, /light=10,state=dark/);
});

test("06-motion-gestures reports tilt and shake", async ({ page }) => {
  await flash(page, "06-motion-gestures");
  await waitForSerial(page, /tilt=/);
  await setValue(page, "accelerometerX", 800);
  await waitForSerial(page, /x=800,.*tilt=right/);
  await setValue(page, "gesture", "shake");
  await waitForSerial(page, /shake!/);
  await setValue(page, "gesture", "none");   // the Python Editor UI also resets to "none"
  expect(await page.evaluate(() => window.sim.errors)).toEqual([]);
});
