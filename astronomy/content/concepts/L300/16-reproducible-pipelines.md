**Concept: reproducible pipelines - provenance, content-addressed caching and versioned inputs**

## Why it matters
Astronomical results come from chains of steps over data that keeps changing: reprocessed releases, corrected timestamps, new calibrations. Caching makes the chain fast enough to iterate on. The danger is a cache that answers "have I seen this **name** before?" instead of "have I seen this **content** before?". Then a corrected release silently returns yesterday's wrong answer, and the published period is an alias.

## Mental model
Every result is a function of exactly three things: its input bytes, the code, and the parameters. Hash all three, and the hash is the result's identity. Write down which hash produced which, and you can always answer "where did this number come from?".

```
input bytes --sha256--+
step source --sha256--+--> key --> cache/<key>.json      prov.jsonl:
params (JSON) --------+                                   activity, used(sha), params,
                                                          code_sha, generated_sha, hit/miss
```

## How it works
1. **Steps as pure functions.** load → detrend(window) → best_period. Each takes data and parameters and returns data; nothing reads hidden state → see lab step 1.
2. **Provenance records.** One JSON line per step run: the activity, the used entity and its SHA-256, the parameters, the code hash, the generated hash and whether the cache hit. This is the W3C PROV idea (activity, used, wasGeneratedBy), and the IVOA Provenance model builds on it → see lab step 2.
3. **Content-addressed keys.** Key = hash(step name, step source, upstream data, parameters). A new release, an edited step or a changed parameter changes the key; an identical rerun hits → see lab step 4.
4. **Versioned inputs.** Releases keep their file names, so record the input hash with every result, and keep old releases next to new ones (`lightcurve_v1.csv`, `_v2.csv`) → see lab step 3.
5. **Hidden inputs.** Module constants, environment variables and library versions are inputs too. Pass them as parameters or hash them → see lab step 5.

**Worked example (lab run):** v1 (half the times 0.5 d late, a JD/MJD mix-up) gives an alias of 0.43049 d at power 0.5201. With the shipped name-based key, v2 also returns 0.43049 d: both steps report `"cache": "hit"` while the log shows the input hash changed from `4c4576852c83` to `6141395bece9`. With content-addressed keys, v2 misses twice and returns 0.30112 d at power 0.882 (truth 0.3011 d). In tryIt 2, changing the module-level frequency grid still hits, and the answer is stale.

## Failure modes
- **Name-keyed caches**, including `joblib.Memory` called with a path: correct until the file changes. Detect it by logging input hashes next to hit/miss.
- **Partial keys.** A parameter only in the first step's key leaves downstream steps stale (tryIt 1: window 5 → 1, `best_period` hits).
- **Hidden state.** Globals, the current date and unpinned libraries. Two machines then disagree, and nobody can say why.
- **Unbounded caches.** Content addressing never overwrites, so disk use only grows. Add eviction by age or size.

## Common mistakes
- Hashing the file name or modification time instead of the bytes.
- Logging provenance after the fact from memory instead of at run time from the actual hashes.
- Overwriting `data/lightcurve.csv` in place with no version suffix or checksum.
