// Offline check of host.html's script (no browser, no network): runs the inline
// <script> in Node's vm with a tiny fake DOM and fake simulator iframes, then checks
// the radio bridge (radio_output -> radio_input, group filter) and the origin checks.
// Run: node host-bridge.check.js   (part of `npm run check`)
const fs = require("fs");
const path = require("path");
const vm = require("vm");
const assert = require("assert");

const html = fs.readFileSync(path.join(__dirname, "host.html"), "utf8");
const script = html.match(/<script>([\s\S]*?)<\/script>/)[1];
const ORIGIN = "https://python-simulator.usermbit.org";

const listeners = [];
const iframes = [];
const fakeDocument = {
  createElement(tag) {
    const el = { tag, textContent: "", posted: [], set src(v) { this._src = v; } };
    if (tag === "iframe") {
      el.contentWindow = { postMessage: (msg, origin) => el.posted.push({ msg, origin }) };
      iframes.push(el);
    }
    return el;
  },
  getElementById() { return { append() {} }; },
};
const win = { addEventListener: (type, fn) => type === "message" && listeners.push(fn) };
const ctx = { window: win, document: fakeDocument, location: { search: "?boards=2" },
  URL, URLSearchParams, TextEncoder, Uint8Array, Math, Number, String, Object, Array };
vm.runInNewContext(script, ctx);

const sims = win.sims;
const emit = (i, data, origin = ORIGIN) =>
  listeners.forEach((fn) => fn({ origin, source: iframes[i].contentWindow, data }));

assert.strictEqual(sims.length, 2);
assert.strictEqual(win.sim, sims[0]);
emit(0, { kind: "ready", state: { radio: { enabled: true, group: 7 } } });
emit(1, { kind: "ready", state: { radio: { enabled: true, group: 7 } } });

// same group: board 0's packet reaches board 1 only, posted to the exact origin
const pkt = new Uint8Array([1, 0, 1, 98, 116, 110]);
emit(0, { kind: "radio_output", data: pkt });
const toB = iframes[1].posted.filter((p) => p.msg.kind === "radio_input");
assert.strictEqual(toB.length, 1);
assert.strictEqual(toB[0].origin, ORIGIN);
assert.deepStrictEqual(Array.from(toB[0].msg.data), Array.from(pkt));
assert.strictEqual(iframes[0].posted.filter((p) => p.msg.kind === "radio_input").length, 0);

// different group: dropped by the bridge
emit(1, { kind: "state_change", change: { radio: { enabled: true, group: 8 } } });
emit(0, { kind: "radio_output", data: pkt });
assert.strictEqual(iframes[1].posted.filter((p) => p.msg.kind === "radio_input").length, 1);

// wrong origin or wrong source window: ignored
emit(0, { kind: "serial_output", data: "evil" }, "https://example.org");
listeners.forEach((fn) => fn({ origin: ORIGIN, source: {}, data: { kind: "serial_output", data: "x" } }));
assert.strictEqual(sims[0].serial, "");
emit(0, { kind: "serial_output", data: "ok\r\n" });
assert.strictEqual(sims[0].serial, "ok\r\n");

// log_output is recorded, not required
emit(0, { kind: "log_output", headings: ["Time (seconds)", "temp"], data: ["0.00", "21"] });
assert.strictEqual(sims[0].logOutput.length, 1);
console.log("host.html bridge check: OK (2 boards, group filter, origin checks, log_output recorded)");
