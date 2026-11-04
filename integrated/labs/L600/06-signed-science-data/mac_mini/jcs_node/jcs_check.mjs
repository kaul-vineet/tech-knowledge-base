// Cross-language JCS (RFC 8785) for L600 #06: reads vectors [{id, text}] from argv[2], prints one JSON line per vector
// {id, hex} with the canonical UTF-8 bytes in hex. argv[3] picks the implementation:
//   builtin       RFC 8785's own recipe in ECMAScript: primitives via JSON.stringify (Number::toString for doubles),
//                 object keys sorted with the default sort, which compares UTF-16 code units (RFC 8785 section 3.2.3)
//   canonicalize  the npm package `canonicalize` (Apache-2.0), installed with `npm ci` / `npm install` in this folder
import { readFileSync } from "node:fs";

function builtin(v) {
  if (v === null || typeof v !== "object") return JSON.stringify(v);
  if (Array.isArray(v)) return "[" + v.map(builtin).join(",") + "]";
  return "{" + Object.keys(v).sort().map((k) => JSON.stringify(k) + ":" + builtin(v[k])).join(",") + "}";
}

const [, , file, impl = "builtin"] = process.argv;
let canon = builtin;
if (impl === "canonicalize") canon = (await import("canonicalize")).default;
for (const { id, text } of JSON.parse(readFileSync(file, "utf8"))) {
  const out = canon(JSON.parse(text));
  console.log(JSON.stringify({ id, impl, hex: Buffer.from(out, "utf8").toString("hex") }));
}
