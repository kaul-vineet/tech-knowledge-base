// L400 device programs in the real MicroPython simulator (pending-ci: needs internet).
// The L400 numbers (delivery, attacks, drift) come from the CPython stub; here we check that the
// device code runs in MicroPython and RECORD what the stub cannot know (e.g. SipHash time per tag).
const { test, expect } = require("@playwright/test");
const { openSimulator, flashCode, labCode, setValue, serialOf, waitForSerial } = require("./sim-helpers");

test("17-edge-to-cloud solution: a sensor reading crosses the relay as a lab 15 serial frame", async ({ page }) => {
  await openSimulator(page, 2);
  const code = labCode("17-edge-to-cloud", "solution.py");
  const relay = code.replace("if __name__ == \"__main__\":\n    main()", "if __name__ == \"__main__\":\n    main(\"relay\", \"relay\")");
  expect(relay).not.toBe(code);
  await flashCode(page, relay, 0);
  await setValue(page, "temperature", 21, 1);
  await flashCode(page, code, 1);                       // sensor n1
  await waitForSerial(page, /\$\d{3}n1,1,\d+,21,\d+,[01]\*[0-9A-F]{4}/, 30_000, 0);
});

test("18-fleet-config solution: the two-phase agent starts and stays up", async ({ page }) => {
  await openSimulator(page);
  await flashCode(page, labCode("18-fleet-config", "solution.py"));
  await page.waitForTimeout(3_000);
  expect(await serialOf(page)).not.toMatch(/Traceback/);
});

test("19-radio-auth frame_auth: SipHash-2-4 reference vector and time per tag in MicroPython (record)", async ({ page }) => {
  await openSimulator(page);
  const code = labCode("19-radio-auth", "frame_auth.py") +
    "\nfrom microbit import running_time\n" +
    "t0 = running_time()\nfor _ in range(20):\n    h = siphash24(bytes(range(16)), bytes(range(15)))\n" +
    "print('siphash', hex(h), (running_time() - t0) // 20, 'ms/tag')\n";
  await flashCode(page, code);
  await waitForSerial(page, /siphash 0xa129ca6149be45e5 \d+ ms\/tag/, 60_000);
  const line = (await serialOf(page)).match(/siphash .*/)[0];
  test.info().annotations.push({ type: "SipHash-2-4 in MicroPython", description: line });
});

test("21-edge-ai-explain firmware_alarm: runs at 31 C without errors", async ({ page }) => {
  await openSimulator(page);
  await setValue(page, "temperature", 31);
  await flashCode(page, labCode("21-edge-ai-explain", "firmware_alarm.py"));
  await page.waitForTimeout(3_000);
  expect(await serialOf(page)).not.toMatch(/Traceback/);
});
