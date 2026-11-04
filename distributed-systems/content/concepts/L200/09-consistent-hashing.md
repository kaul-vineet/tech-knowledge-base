## Why it matters
A cache cluster grows from 4 to 5 servers. With `hash(key) % N` about 80% of keys move to a different server: the hit rate collapses and the database takes the load. Consistent hashing moves only the keys the new server should own.

## Mental model
Nodes and keys sit on one circle of hash values; a key belongs to the first node point clockwise. A new node takes only the arcs just before its points.

```
          A#17
      .----*----.        key k hashes here
   D#2 *          * B#3  <- first point clockwise: owner B
      '--*-----*--'
       C#40   A#5        each node = 100 points (vnodes)
```

## How it works
1. **Hash keys and nodes onto one ring** with a stable hash (md5 here); Python's `hash()` is salted per process. → see lab step 1
2. **Owner = next point clockwise**: binary search in the sorted points, wrapping at the end. → see lab step 1
3. **Joins and leaves move about 1/N of the keys**, only to or from the changed node. → see lab step 2
4. **Virtual nodes even out the load**: one point per node leaves very unequal arcs, 100 points average them out. → see lab step 3
5. **Hashing does not fix hot keys.** One popular key lives on one node; split or replicate it. → see lab step 4

Worked example (demo output, 10,000 keys): from 4 to 5 nodes, `hash % N` moves 80.3% of keys, the ring 18.9% (ideal 20%). With 1 vnode per node the busiest node holds 2.20× the average; with 100, 1.03×. A key taking 20% of requests still pushes its node to 1.59×.

## Trade-offs
| Use it when | Avoid it when |
|---|---|
| Nodes join and leave and moving data is expensive | The node set never changes: modulo is simpler |
| Clients route without a central directory | You need range scans over ordered keys |

More vnodes: smoother load, but more ring metadata and more neighbours per node in replicated stores.

## Common mistakes
- A randomized built-in hash: every process builds a different ring.
- One point per node, so one server holds half the data.
- Expecting the ring to fix a hot key.
