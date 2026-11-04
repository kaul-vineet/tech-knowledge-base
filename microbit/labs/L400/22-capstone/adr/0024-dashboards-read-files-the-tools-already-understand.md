# ADR 0024: Dashboards read exports in formats the catalog tools understand

## Status
Accepted (2026-10-28); the tool-side setup is a manual, pending step.

## Context
The learning-tools catalog offers Apache Superset (CSV upload; no official Windows support, Docker
unofficial) and Grafana OSS (Prometheus/PostgreSQL data sources; no CSV source in core), plus
Prometheus. Running a database server for a classroom monitor is heavy, and the labs must run with the
Python standard library only.

## Decision
We will store readings in SQLite and export two files per run: `dashboard.csv` (one row per reading)
for Superset's CSV upload, and `metrics.txt` in the Prometheus text exposition format (# HELP / # TYPE /
name{labels} value), served as text/plain on 127.0.0.1 for a Prometheus scrape that Grafana reads.
A milestone test checks that both exports agree with the store (3,599 rows on seed 22).

## Consequences
No server is needed for the labs; the dashboards are one manual step away on the Mac mini (Superset via
Docker/pip, Grafana via Homebrew) and on Windows (Grafana installer; Superset only via unofficial Docker).
Exports are snapshots, not live streams: a live dashboard would scrape a running gateway's endpoint.
