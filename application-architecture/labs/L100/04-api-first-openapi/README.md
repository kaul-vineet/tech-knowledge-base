# Lab 04 – API-first with OpenAPI 3.1

Write the contract (`openapi.json`, OpenAPI 3.1.2) first, then implement it with
`http.server`, then test that real responses match the spec's paths, status codes and
required fields.

**Why 3.1 and not 3.2.x?** spec.openapis.org lists 3.2.1 and 3.2.0. The lab uses no 3.2-only feature (such as the `query`
method), minor OpenAPI versions may contain incompatible changes (OAS 3.2.0 §2.1), and the tools this lesson points to
(Swagger Editor exercise, Bruno import) are catalogued for 3.1. Move to 3.2 once your validator and generators accept it.

## Files
| File | Purpose |
|---|---|
| `openapi.json` | The contract: `/health`, `POST /loans`, `GET /loans/{loanId}` |
| `server.py` | stdlib implementation (in-memory) |
| `contract_check.py` | Minimal checker: path+method declared, status declared, required fields + JSON types + enum |
| `test_contract.py` | Starts the server on a free port, calls every operation, checks each response; proves the checker catches drift |
| `client_demo.py` | Calls a running server and prints each response with its contract result |
| `try_it.py` | Runs the lesson's two tryIt experiments and prints what happened (never edits the lab files) |

## Run
```bash
cd labs/L100/04-api-first-openapi
python -m unittest -v
# manual run: terminal 1                      terminal 2
python server.py 18765                        # python client_demo.py 18765
```

## Expected output (observed 2026-10-28, Python 3.12.15)
```
test_undeclared_status_and_bad_body_are_reported (test_contract.CheckerCatchesDriftTest.test_undeclared_status_and_bad_body_are_reported) ... ok
test_every_declared_response_is_exercised (test_contract.ContractTest.test_every_declared_response_is_exercised) ... ok
test_responses_match_spec (test_contract.ContractTest.test_responses_match_spec) ... ok
test_required_top_level_fields (test_contract.SpecShapeTest.test_required_top_level_fields) ... ok

----------------------------------------------------------------------
Ran 4 tests in 1.406s

OK
```
`python client_demo.py 18765` against a fresh `python server.py 18765`:
```
GET  /health   -> 200 {'status': 'ok'}  contract: OK
POST /loans    -> 201 {'id': 1, 'bookId': 'b1', 'memberId': 'm1', 'status': 'active'}  contract: OK
POST /loans    -> 409 {'error': 'book b1 is already on loan'}  contract: OK
GET  /loans/1  -> 200 {'id': 1, 'bookId': 'b1', 'memberId': 'm1', 'status': 'active'}  contract: OK
```

## Same idea in maintained tools
- Schemathesis (MIT): generates requests from an OpenAPI/GraphQL schema and checks responses (`schemathesis run <url>/openapi.json`) – point it at dev/staging, not production.
- Pact: consumer-driven contract tests ("contract by example") – complements, not replaces, schema checks.

## Try it (observed 2026-10-28, Python 3.12.15)
Predict first, then run. `try_it.py` never edits the lab files (code changes go to a temporary `.tryit-work/` copy that is deleted afterwards); the tasks and predictions are in the lesson's `tryIt` field.
```bash
python try_it.py
```
```
[1] memberId renamed to member -> exit 1; FAILED (failures=2)
    FAIL: test_responses_match_spec (test_contract.ContractTest.test_responses_match_spec) (method='POST', path='/loans', expected=201)
    AssertionError: Lists differ: ["POST /loans 201: missing required field 'memberId'"] != []
    FAIL: test_responses_match_spec (test_contract.ContractTest.test_responses_match_spec) (method='GET', path='/loans/1', expected=200)
    AssertionError: Lists differ: ["GET /loans/{loanId} 200: missing required field 'memberId'"] != []
[2] POST /loans answered 500 -> ['POST /loans: status 500 not declared']
[2] POST /loans answered 409 -> []
```

## Troubleshooting
| Symptom | Action |
|---|---|
| `OSError: [Errno 98] Address already in use` (macOS: `[Errno 48]`, Windows: `[WinError 10048]`) | Another process has that port (we hit this with 8765 and 8000 on a shared machine); pass a different port: `python server.py 18765`. Tests always use port 0 (any free port). |
| `status 404 not declared` for every call in `client_demo.py` | You are talking to a different server on that port; check the port printed by `server.py`. |
