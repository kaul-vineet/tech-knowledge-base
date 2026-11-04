# Learning tools – Application Architecture

Open-source tools from the KB catalogue (`../../shared/LEARNING-TOOLS-CATALOG.md` + `learning-tools.json`, checked 2026-10-28).
Names below match the catalogue exactly. Roles: SEE = visualise · BUILD WITHOUT CODE = prototype · CHECK = compare with your code · INSPECT = look inside.
Each lesson's `learningTools` field holds the exercise and the lab value to compare with (max 2 per lesson).

| Tool | Role | Licence (OSI) | Mac mini install | Windows install | Lessons |
|---|---|---|---|---|---|
| Structurizr (local) | SEE | Apache-2.0, open-core (yes) | `docker run -it --rm -p 8080:8080 -v PATH:/usr/local/structurizr structurizr/structurizr local` | same | 6, 17, 22 |
| Swagger Editor v5 / Swagger UI | CHECK / SEE | Apache-2.0 (yes) | browser, or `docker run -p 8080:80 docker.swagger.io/swaggerapi/swagger-editor:latest` | same | 4, 20 |
| AsyncAPI Studio | SEE / CHECK | Apache-2.0 (yes) | browser; self-built Docker image | same | 9 |
| Bruno | CHECK | MIT, open-core (yes) | `brew install --cask bruno` | `winget install Bruno.Bruno` | 4, 11, 14, 22 |
| Keycloak | SEE / BUILD WITHOUT CODE | Apache-2.0 (yes) | `docker run -p 127.0.0.1:8080:8080 -e KC_BOOTSTRAP_ADMIN_USERNAME=admin -e KC_BOOTSTRAP_ADMIN_PASSWORD=admin quay.io/keycloak/keycloak:26.8.1 start-dev` | same container, or zip: `bin\kc.bat start-dev` | 10, 19 |
| import-linter | CHECK / SEE | BSD-2-Clause (yes) | `pip install import-linter` | same | 3, 7, 16, 17 |
| marimo | CHECK / SEE | Apache-2.0 (yes) | `pip install marimo` | same | 12 |
| Toxiproxy | BUILD WITHOUT CODE | MIT (yes) | `brew tap shopify/shopify && brew install toxiproxy` | `toxiproxy-server`/`cli-windows-amd64.exe` from the releases | 13 |
| Pact Broker (OSS) | SEE / CHECK | MIT (yes) | `docker run -p 9292:9292` with `PACT_BROKER_DATABASE_ADAPTER=sqlite` (arm64 image) | partial: same container via Docker Desktop (Linux-only image) | 14 |
| JupyterLab (+ JupyterLab Desktop) | CHECK / SEE | BSD-3-Clause (yes) | `pip install jupyterlab` (or Desktop installer) | same (or `winget install jupyterlab`) | 15, 18, 20, 21 |
| Prometheus (+ expression browser, promtool) | CHECK | Apache-2.0 (yes) | `prometheus-3.15.1.darwin-arm64.tar.gz` (includes promtool) | `prometheus-3.15.1.windows-amd64.zip` | 15, 22 |
| Grafana k6 | CHECK | AGPL-3.0 (yes) | `brew install k6` | `winget install k6 --source winget` | 16, 21 |

Containers: Podman (`../../shared/WORKSTATION-SETUP.md`) runs the same images.

## How to use these tools
They complement the labs; you still write and run the code. Use a tool to *see* a concept, to *prototype* without
code, or to *check* your result against the lab's printed value. When tool and lab disagree, find out why.
No exercise ran in the sandbox (no container engine, no pip), so each `expected` names the lab output to match.
L400: OPA 1.21.4 (Apache-2.0) is not catalogued; lesson 19 uses it only as the CI engine for the same policy file.

## Not recommended / changed
- **Grafana OSS (lesson 15)** – replaced by Prometheus `promtool test rules`: Grafana core has no CSV/JSON-lines source, so it could only start
  from TestData; promtool checks the real burn-rate maths. If you use Grafana elsewhere, pick the Open Source edition (AGPL-3.0), not Enterprise.
- **PactFlow** – the commercial fork of Pact Broker; not used. The broker's SQLite mode is for spikes only (data lost with the container).
- **Perses / Grafana Tempo / Zipkin** – dropped L300 candidates: duplicate Grafana or Jaeger; Perses is pre-1.0 and 0.55.0 fixed critical unauthenticated issues.
- **Structurizr Lite** – archived 2026-02-04; use `structurizr/structurizr local`.
- **draw.io Desktop** – now GPL-3.0 (31.5.2); optional, our diagrams stay as text.
- **Mermaid C4** – still experimental; lesson 6 keeps Structurizr DSL.
- **Bruno for OAuth2/PKCE** – free-tier support not confirmed; use Hoppscotch (MIT) for lesson 10 if needed.
- **jwt.io debugger** – proprietary; decode lesson 10's tokens with CyberChef (Apache-2.0) instead.
- **Archi** – ArchiMate, not C4: low fit.
