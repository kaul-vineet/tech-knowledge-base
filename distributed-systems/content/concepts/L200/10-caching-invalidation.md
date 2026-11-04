## Why it matters
A product page reads prices from a 200 ms database. A cache makes most reads instant — until a price changes and the cache serves the old one, or a popular key expires and 50 requests hit the database at once.

## Mental model
The cache is a sticky note copied from the master file: fast to read, possibly out of date, torn off when the file changes. If fifty people find no note at the same moment, all fifty walk to the filing cabinet.

```
read : cache hit? --yes--> value
           | no
       database --> cache it (TTL 30 s) --> value
write: database = new value, then DELETE the key
```

## How it works
1. **Cache-aside.** Check the cache; on a miss read the database and store the result with a TTL. → see lab step 1
2. **The TTL bounds staleness**: without invalidation a changed value is served until expiry. → see lab step 2
3. **Invalidate on write.** Write the database, then delete the key; the next read refetches. Deletes beat updates because they are idempotent. → see lab step 3
4. **Thundering herd.** When a hot key is missing, every concurrent request goes to the database. → see lab step 4
5. **Request coalescing.** One request per key loads; the others wait for its result. → see lab step 6

Worked example (demo output): with a 30 s TTL and no invalidation the old price 5 was served at t=0, 10 and 29 s, the new price 7 from t=30. Fifty concurrent reads of a cold key made 50 database reads; with coalescing, 1.

## Trade-offs
| Use it when | Avoid it when |
|---|---|
| Reads far outnumber writes and slight staleness is fine | Every read must see the latest write |
| The source is slow or expensive | Values change on almost every read |

Long TTL: fewer database reads, longer staleness (tryIt 1: 30 s gave 30 stale of 60 reads and 2 DB reads; 5 s gave 5 and 12).

## Common mistakes
- Updating the cache on write instead of deleting: two writers can leave the older value.
- Trusting invalidation alone: a slow reader can re-insert an old value after the delete (tryIt 2); keep a TTL.
- One TTL for many keys loaded together, so they expire together.
