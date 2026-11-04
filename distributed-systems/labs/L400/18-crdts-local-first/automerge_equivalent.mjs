// Lab 18 equivalent with Automerge 3.3.2 (MIT, npm @automerge/automerge) - an op-based JSON CRDT.
// Run (Node 24):  npm install  then  node automerge_equivalent.mjs   (pending-ci: not run in the authoring sandbox)
// Same stories as crdts.py: concurrent edits on two devices merge to the same document; a CRDT counter keeps
// concurrent increments (PN-Counter); concurrent writes to one field converge and Automerge keeps the losing value
// as a conflict (LWW-Register with a deterministic tie-break).
import * as A from "@automerge/automerge";
import assert from "node:assert/strict";

let phone = A.from({ items: { milk: true }, likes: new A.Counter(0), title: "groceries" });
let laptop = A.clone(phone);

phone = A.change(phone, (d) => { delete d.items.milk; d.likes.increment(2); d.title = "weekend"; });
laptop = A.change(laptop, (d) => { d.items.eggs = true; d.likes.increment(3); d.title = "party"; });

const a = A.merge(A.clone(phone), laptop);
const b = A.merge(A.clone(laptop), phone);

assert.deepEqual(A.toJS(a), A.toJS(b)); // converged: same document on both devices
assert.equal(a.likes.value, 5); // concurrent increments add up, like the PN-Counter (truth 2 + 3)
assert.equal(Object.keys(A.getConflicts(a, "title")).length, 2); // both concurrent titles are kept as a conflict
console.log(JSON.stringify({ converged: true, items: Object.keys(a.items).sort(), likes: a.likes.value,
  title: a.title, titleConflicts: Object.values(A.getConflicts(a, "title")).sort() }));
