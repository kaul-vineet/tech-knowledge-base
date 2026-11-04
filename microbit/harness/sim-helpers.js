// Helpers that drive window.sims (see host.html) from Playwright tests.
// Every function takes an optional board index (default 0 = window.sim).
const fs = require("fs");
const path = require("path");

const LABS = path.join(__dirname, "..", "labs");

// Lab ids are unique across levels: "03-buttons" is in L100, "07-radio" in L200, "12-reliable-radio" in L300,
// "17-edge-to-cloud" in L400.
function labDir(labId) {
  for (const level of ["L100", "L200", "L300", "L400"]) {
    const dir = path.join(LABS, level, labId);
    if (fs.existsSync(dir)) return dir;
  }
  throw new Error(`no lab ${labId} in labs/L100, labs/L200, labs/L300 or labs/L400`);
}

function labCode(labId, file = "main.py") {
  return fs.readFileSync(path.join(labDir(labId), file), "utf8");
}

async function openSimulator(page, boards = 1) {
  const q = new URLSearchParams();
  if (process.env.SIM_URL) q.set("sim", process.env.SIM_URL);
  if (boards > 1) q.set("boards", String(boards));
  const qs = q.toString();
  await page.goto(`/${qs ? "?" + qs : ""}`);
  await page.waitForFunction((n) => window.sims && window.sims.length === n && window.sims.every((s) => s.ready),
    boards, { timeout: 60_000 });
  await page.evaluate(() => window.sims.forEach((s) => s.mute()));   // headless CI: no audio needed
}

async function flash(page, labId, board = 0) {
  await flashCode(page, labCode(labId), board);
}

async function flashCode(page, code, board = 0) {
  await page.evaluate(([c, b]) => window.sims[b].flash(c), [code, board]);
}

// A lab's main.py with a tryIt variant applied (same [old, new] replacements
// as labs/sim_stub/tryit.py reads from the lab's try_it.json).
function variantCode(labId, name) {
  const { variants } = JSON.parse(fs.readFileSync(path.join(labDir(labId), "try_it.json"), "utf8"));
  let code = labCode(labId);
  for (const [oldText, newText] of variants[name]) {
    if (code.split(oldText).length !== 2) throw new Error(`${labId}/${name}: ${oldText} must occur once`);
    code = code.replace(oldText, () => newText);
  }
  return code;
}

async function setValue(page, id, value, board = 0) {
  await page.evaluate(([i, v, b]) => window.sims[b].set(i, v), [id, value, board]);
}

// Press and release a button (ids: "buttonA", "buttonB") or touch pin ("pinLogo", "pin0").
async function click(page, id, holdMs = 150, board = 0) {
  await setValue(page, id, 1, board);
  await page.waitForTimeout(holdMs);
  await setValue(page, id, 0, board);
  await page.waitForTimeout(holdMs);
}

async function serialOf(page, board = 0) {
  return page.evaluate((b) => window.sims[b].serial, board);
}

// Wait until the accumulated serial text of a board matches `pattern` (RegExp).
async function waitForSerial(page, pattern, timeout = 20_000, board = 0) {
  try {
    await page.waitForFunction(
      ([src, flags, b]) => new RegExp(src, flags).test(window.sims[b].serial),
      [pattern.source, pattern.flags, board],
      { timeout }
    );
  } catch (err) {
    const serial = await serialOf(page, board);
    const errors = await page.evaluate((b) => window.sims[b].errors, board);
    throw new Error(`board ${board}: serial never matched ${pattern}\n--- serial ---\n${serial}\n--- errors ---\n${errors.join("\n")}`);
  }
}

module.exports = {
  labDir, labCode, variantCode, openSimulator, flash, flashCode, setValue, click, serialOf, waitForSerial,
};
