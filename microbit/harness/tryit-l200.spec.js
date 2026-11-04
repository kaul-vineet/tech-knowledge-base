// Simulator confirmation of the L200 tryIt items (pending-ci).
// Same try_it.json edits as each lab's try_it.py. Not covered here (stub only):
// 08 item 2 (export_csv.py runs on the PC), 10 item 2 (needs an I2C device; the
// simulator has none), 11 item 2 (depends on exact press timing).
const { test, expect } = require("@playwright/test");
const { openSimulator, flash, flashCode, variantCode, setValue, click, serialOf, waitForSerial } = require("./sim-helpers");

test("tryIt 07 group-8: board 1 on group 8 hears nothing from group 7", async ({ page }) => {
  await openSimulator(page, 2);
  await flash(page, "07-radio", 0);
  await flashCode(page, variantCode("07-radio", "group-8"), 1);
  await waitForSerial(page, /radio group 7/, 20_000, 0);
  await waitForSerial(page, /radio group 8/, 20_000, 1);
  const groups = await page.evaluate(() => window.sims.map((s) => s.state && s.state.radio));
  test.info().annotations.push({ type: "radio state", description: JSON.stringify(groups) });
  await click(page, "buttonA", 150, 0);
  await waitForSerial(page, /tx btn 1 A/, 20_000, 0);
  await page.waitForTimeout(1_500);
  expect(await serialOf(page, 1)).not.toMatch(/rx /);
});

test("tryIt 07 long-value: 40 characters are cut to a 32-byte packet", async ({ page }) => {
  await openSimulator(page, 2);
  const code = variantCode("07-radio", "long-value");
  await flashCode(page, code, 0);
  await flashCode(page, code, 1);
  await waitForSerial(page, /radio group 7/, 20_000, 1);
  await click(page, "buttonA", 150, 0);
  await waitForSerial(page, /rx btn 1 A{23}\r?\n/, 20_000, 1);
  expect(await page.evaluate(() => window.sims[0].radioOut[0].length)).toBe(32);
});

test("tryIt 08 mirroring-on: rows also appear in log-module format", async ({ page }) => {
  await openSimulator(page);
  await flashCode(page, variantCode("08-data-logging", "mirroring-on"));
  await waitForSerial(page, /time_ms,temp,light/);
  await waitForSerial(page, /Time \(seconds\),temp,light/);
  await waitForSerial(page, /\d+\.\d\d,\d+,\d+/);
});

test("tryIt 09 no-edge: holding the logo keeps toggling", async ({ page }) => {
  await openSimulator(page);
  await flashCode(page, variantCode("09-pins-pwm", "no-edge"));
  await waitForSerial(page, /on=0,level=2,duty=0/);
  await setValue(page, "pinLogo", 1);
  await waitForSerial(page, /on=1[\s\S]*on=0[\s\S]*on=1/);
  await setValue(page, "pinLogo", 0);
});

test("tryIt 09 levels-3: level 2 of 3 is duty 682", async ({ page }) => {
  await openSimulator(page);
  await flashCode(page, variantCode("09-pins-pwm", "levels-3"));
  await waitForSerial(page, /on=0,level=2,duty=0/);
  await click(page, "pinLogo");
  await waitForSerial(page, /on=1,level=2,duty=682/);
});

test("tryIt 10 addr-0x49: the error names the address the code used", async ({ page }) => {
  await openSimulator(page);
  await flashCode(page, variantCode("10-i2c-sensor", "addr-0x49"));
  await waitForSerial(page, /i2c: no device at 0x49 \(errno \d+\)|temp_c=/);
});

test("tryIt 11 no-shake-abort: shake during play is ignored", async ({ page }) => {
  await openSimulator(page);
  await flashCode(page, variantCode("11-game-state-machine", "no-shake-abort"));
  await waitForSerial(page, /game ready/);
  await click(page, "buttonA");
  await waitForSerial(page, /idle -> play \(a\)/);
  await setValue(page, "gesture", "shake");
  await page.waitForTimeout(1_000);
  await setValue(page, "gesture", "none");
  expect(await serialOf(page)).not.toMatch(/play -> idle/);
});
