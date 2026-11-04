# ADR 1: Store loans in SQLite behind a repository interface

## Context

The Library Loans service started with an in-memory dictionary, which loses every loan
when the process restarts. The service runs as a single process for one library branch,
and the team wants to keep the codebase standard-library only so that labs and CI need
no package downloads. Loan rules (one active loan per book, a per-member limit) must stay
testable without a database server. A later move to a client-server database is
possible but not planned.

## Decision

We will store loans in SQLite through Python's built-in `sqlite3` module. All SQL lives
in one repository class that has the same methods as the in-memory repository
(`add`, `get`, `active`, `mark_returned`). The service layer receives a repository
object and never imports `sqlite3`. The concrete repository is chosen in one wiring
function at startup, and the database file path comes from the `LOANS_DB_PATH`
environment variable.

## Status

Accepted.

## Consequences

Loans survive restarts and the service still has no third-party dependencies. Rule tests
run against both repositories, so a storage change is checked by the existing suite.
SQLite allows one writer at a time, so this decision must be revisited if several
service instances need to write concurrently; that change should only touch the
repository and wiring code. The connection is opened with `check_same_thread=False`
because the HTTP server calls it from another thread, which means writes must stay
serialized; the current single-threaded `HTTPServer` does that.
