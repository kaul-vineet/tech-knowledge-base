**Concept: configuration as environment, validated at startup**

## Why it matters
The database path is a constant in `settings.py`. Staging overwrites production data because someone
forgot to edit it and another developer commits the SMTP password. Keeping config
out of the code fixes both.

## Mental model
A rental car: the same car for every driver. Seat and mirrors (config) are set when the trip starts
and checked once before driving off.

```
same build ─┬─ dev:  LOANS_DB_PATH=loans.db    LOANS_LOG_LEVEL=DEBUG
            └─ prod: LOANS_DB_PATH=/data/p.db  LOANS_SMTP_PASSWORD=<injected>
load_settings(os.environ) ─► valid? ─yes─► start
                                └─no──► print ALL errors, exit 2
```

## How it works
1. **Config is what varies between deploys** (ports, paths, credentials). It comes from env vars;
   routes and wiring stay in code → see lab step 2
2. **Read once, validate, fail fast.** `load_settings()` builds a frozen `Settings`, collects every
   error, and `app.py` exits 2 before serving traffic → see lab step 3
3. **Secrets are special.** No default in code, `repr=False` keeps them out of logs, and a test scans
   for literal secrets. → see lab step 4

**Worked example** (computed by `research/concept_examples.py`): `LOANS_PORT=70000` with
`LOANS_LOG_LEVEL=warn` gives one message with both errors: the port must be between 1 and 65535, and
`'WARN'` is not one of `['DEBUG', 'ERROR', 'INFO', 'WARNING']`.

## Common mistakes
- Reading `os.environ` all over the code instead of once at startup.
- Giving a secret a "dev" default in code: it ends up in the repo.
- Stopping at the first bad variable, so operators fix one error per deploy.
