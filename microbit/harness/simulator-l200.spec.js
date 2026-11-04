// End-to-end checks: each L200 lab runs in the real MicroPython simulator.
// Requires internet (loads python-simulator.usermbit.org). Run in CI.
// Lab 07 uses TWO simulators in one page, bridged by host.html (radio_output -> radio_input).
const { test, expect } = require("@playwright/test");
const { openSimulator, flash, setValue, click, serialOf, waitForSerial } = require("./sim-helpers");

const NL = String.raw`\r?\n`;

test("07-radio: A on board 0 arrives on board 1, B on board 1 arrives on board 0", async ({ page }) => {
  await openSimulator(page, 2);
  await flash(page, "07-radio", 0);
  await flash(page, "07-radio", 1);
  await waitForSerial(page, /radio group 7/, 20_000, 0);
  await waitForSerial(page, /radio group 7/, 20_000, 1);
  await click(page, "buttonA", 150, 0);
  await waitForSerial(page, /tx btn 1 A/, 20_000, 0);
  await waitForSerial(page, /rx btn 1 A/, 20_000, 1);
  // radio.send(str) puts 0x01 0x00 0x01 in front of the UTF-8 text (README + radio docs)
  const out = await page.evaluate(() => window.sims[0].radioOut[0]);
  expect(out.slice(0, 3)).toEqual([1, 0, 1]);
  expect(String.fromCharCode(...out.slice(3))).toBe("btn:1:A");
  await setValue(page, "temperature", 23, 1);
  await click(page, "buttonB", 150, 1);
  await waitForSerial(page, /rx tmp 1 23/, 20_000, 0);
});

test("08-data-logging prints serial CSV that follows the sliders", async ({ page }) => {
  await openSimulator(page);
  await flash(page, "08-data-logging");
  await waitForSerial(page, /time_ms,temp,light/);
  await setValue(page, "temperature", 25);
  await setValue(page, "lightLevel", 200);
  await waitForSerial(page, /\n\d+,25,200\r?\n/);
  // Record (do not require) what the simulator reports for the log module itself.
  const log = await page.evaluate(() => ({ n: window.sims[0].logOutput.length, first: window.sims[0].logOutput[0] || null }));
  test.info().annotations.push({ type: "log_output messages", description: JSON.stringify(log) });
  expect(await page.evaluate(() => window.sims[0].errors)).toEqual([]);
});

test("09-pins-pwm: logo toggles, A raises the level, pin0 touch boosts", async ({ page }) => {
  await openSimulator(page);
  await flash(page, "09-pins-pwm");
  await waitForSerial(page, /on=0,level=2,duty=0/);
  await click(page, "pinLogo");
  await waitForSerial(page, /on=1,level=2,duty=511/);
  await click(page, "buttonA");
  await waitForSerial(page, /on=1,level=3,duty=767/);
  await setValue(page, "pin0", 1);              // touch state 0/1 is all the README supports
  await waitForSerial(page, /on=1,level=3,duty=1023/);
  await setValue(page, "pin0", 0);
  await waitForSerial(page, new RegExp(`duty=1023${NL}on=1,level=3,duty=767`));
});

test("10-i2c-sensor: no I2C device in the simulator is reported, not a crash", async ({ page }) => {
  await openSimulator(page);
  await flash(page, "10-i2c-sensor");
  await waitForSerial(page, /scan: \[.*\]/);
  await waitForSerial(page, /i2c: no device at 0x48 \(errno \d+\)|temp_c=/);
  const serial = await serialOf(page);
  test.info().annotations.push({ type: "i2c in simulator", description: serial.split(/\r?\n/).slice(0, 3).join(" | ") });
  expect(serial).not.toMatch(/Traceback/);
});

test("11-game-state-machine: idle -> play -> over -> idle, shake starts", async ({ page }) => {
  await openSimulator(page);
  await flash(page, "11-game-state-machine");
  await waitForSerial(page, /game ready/);
  await click(page, "buttonA");
  await waitForSerial(page, /idle -> play \(a\)/);
  await waitForSerial(page, new RegExp(`play -> over \\(timeout\\)${NL}score \\d+`), 15_000);
  await click(page, "buttonA");
  await waitForSerial(page, /over -> idle \(a\)/);
  await setValue(page, "gesture", "shake");
  await waitForSerial(page, /idle -> play \(shake\)/);
  await setValue(page, "gesture", "none");
});
