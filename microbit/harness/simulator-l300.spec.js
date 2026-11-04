// L300 device programs in the real MicroPython simulator (pending-ci: needs internet).
// The L300 FAULTS (radio loss, quick taps on a timeline, battery model, serial noise)
// are injected only in the CPython stub tests; here we check that the same programs
// run in MicroPython and print what the stub predicts on the happy path.
const { test, expect } = require("@playwright/test");
const { openSimulator, flash, flashCode, labCode, setValue, click, serialOf, waitForSerial } = require("./sim-helpers");

// CRC-16/CCITT-FALSE, same as the labs (check value "123456789" -> 0x29B1)
function crc16(text) {
  let crc = 0xffff;
  for (const ch of text) {
    crc ^= ch.charCodeAt(0) << 8;
    for (let i = 0; i < 8; i++) crc = (crc & 0x8000 ? (crc << 1) ^ 0x1021 : crc << 1) & 0xffff;
  }
  return crc;
}

test("12-reliable-radio solution: a reading crosses two bridged boards and is acked", async ({ page }) => {
  expect(crc16("123456789")).toBe(0x29b1);
  await openSimulator(page, 2);
  const code = labCode("12-reliable-radio", "solution.py");
  await flashCode(page, code, 0);
  await flashCode(page, code, 1);
  await waitForSerial(page, /link group 12/, 20_000, 0);
  await waitForSerial(page, /link group 12/, 20_000, 1);
  await setValue(page, "temperature", 23, 0);
  await click(page, "buttonA", 150, 0);
  await waitForSerial(page, /rx 1 23/, 20_000, 1);
  await click(page, "buttonB", 150, 0);                    // sender prints its JSON counters
  await waitForSerial(page, /"acked":1/, 20_000, 0);
  // the frame on air carries a CRC the stub tests also compute
  const out = await page.evaluate(() => window.sims[0].radioOut[0]);
  const text = String.fromCharCode(...out.slice(3));
  const body = text.slice(0, text.lastIndexOf(":"));
  expect(text.slice(-4)).toBe(crc16(body).toString(16).toUpperCase().padStart(4, "0"));
});

test("13-nonblocking-scheduler solution: three quick taps are counted", async ({ page }) => {
  await openSimulator(page);
  await flashCode(page, labCode("13-nonblocking-scheduler", "solution.py"));
  await waitForSerial(page, /tap counter ready/);
  for (let i = 0; i < 3; i++) await click(page, "buttonA", 150);
  await waitForSerial(page, /tap 3/);
  await waitForSerial(page, /\{"t":\d+,"temp":-?\d+,"taps":3\}/);
});

test("13-nonblocking-scheduler main.py: record how many quick taps the blocking loop sees", async ({ page }) => {
  await openSimulator(page);
  await flash(page, "13-nonblocking-scheduler");
  await waitForSerial(page, /tap counter ready/);
  for (let i = 0; i < 3; i++) await click(page, "buttonA", 150);
  await page.waitForTimeout(2_500);
  const taps = ((await serialOf(page)).match(/^tap \d+/gm) || []).length;
  test.info().annotations.push({ type: "blocking loop, 3 quick taps", description: `${taps} counted` });
  expect(taps).toBeLessThanOrEqual(3);
});

test("14-power-budget solution: runs with power.deep_sleep and log (record errors)", async ({ page }) => {
  await openSimulator(page);
  await flashCode(page, labCode("14-power-budget", "solution.py"));
  await page.waitForTimeout(5_000);
  const serial = await serialOf(page);
  test.info().annotations.push({ type: "power module in simulator", description: serial.slice(0, 300) || "(no serial output)" });
  expect(serial).not.toMatch(/Traceback/);
});

test("15-serial-gateway main.py: frames carry a correct length and CRC in MicroPython", async ({ page }) => {
  await openSimulator(page);
  await setValue(page, "temperature", 21);
  await setValue(page, "lightLevel", 120);
  await flash(page, "15-serial-gateway");
  await waitForSerial(page, /\$\d{3}[^*\r\n]*\*[0-9A-F]{4}\r?\n[\s\S]*\$\d{3}/);
  const frames = (await serialOf(page)).match(/\$(\d{3})([^*\r\n]*)\*([0-9A-F]{4})/g);
  for (const f of frames) {
    const [, len, payload, crc] = f.match(/\$(\d{3})([^*]*)\*([0-9A-F]{4})/);
    expect(payload.length).toBe(Number(len));
    expect(crc).toBe(crc16(payload).toString(16).toUpperCase().padStart(4, "0"));
  }
  expect(frames[0]).toMatch(/^\$\d{3}1,21,120\*/);
});
