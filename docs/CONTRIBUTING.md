# Contributing to LLMOps Dashboard

Thank you for your interest in contributing to **LLMOps Dashboard**!

---

## Local Development Setup

### 1. Clone & Initialize

```bash
git clone https://github.com/Cre4T3Tiv3/llmops-dashboard.git
cd llmops-dashboard
make init
```

This handles:

*System checks for Docker, Compose, SQLite3, etc. via `make check`
* Installs `uv` if missing (modern Python manager)
* Creates a virtual environment
* Installs editable package with `[dev]` extras
* Auto-copies `.env.example` → `.env` (if not already present)
* Verifies `ollama` is installed and the local model (e.g. `llama3`) is available

> ℹ️ Rerun `make check` anytime to verify your local setup.

### 2. Launch Dev Stack

```bash
make dev
```

Brings up the FastAPI (w/ --reload), Prometheus, and Grafana services via Docker Compose.

> ℹ️ Loads environment variables from `.env` and mounts local source for hot reload

---

## Full Test Suite

### Run all tests

```bash
make test
```

### Individually:

```bash
make test-unit     # Only unit tests (fast, logic validation)
make test-e2e      # E2E flows (route → DB → metrics)
make simulate      # Simulated traffic to trigger metrics
make smoke-test    # API/metrics/db integration in one test
```

✅ All tests use a local SQLite DB
✅ JWT tokens auto-generated from `.env`
✅ Docker + services required for E2E

---

## Contributing Scope

Here’s where you can plug in:

| Path                           | What It Covers                            |
| ------------------------------ | ----------------------------------------- |
| `llmops/mcp/`                  | Model registry, policy, client tracking   |
| `llmops/routes/`               | FastAPI routes for echo/proxy/token       |
| `llmops/database.py`          | SQLite schema + ORM logic                 |
| `tests/unit/`                 | Isolated validation (unit)                |
| `tests/e2e/`                  | Full-stack tests (API, DB, metrics)       |
| `grafana/dashboards/`         | LLMOps overview JSON (auto-loaded)        |
| `Makefile`                    | Dev/test/lint toolchain                   |
| `.env / .env.example`         | Auth + env setup                          |
| `docker-compose.yaml`         | Runtime orchestration                     |

---

## Makefile UX Reference

| Command                 | Description                                  |
| ----------------------- | -------------------------------------------- |
| `make init`             | Setup everything: venv, uv, .env, deps       |
| `make up`               | Build and start containers                   |
| `make down`             | Stop containers, preserve volumes            |
| `make clean`            | Full teardown + `.venv` and DB removal       |
| `make nuke`             | Hard reset: volumes, images, cache, DB       |
| `make generate-jwt`     | Print valid token (uses JWT_SECRET)          |
| `make logs`             | Tail FastAPI logs                            |
| `make shell`            | Enter running container for debugging        |
| `make reset-prometheus` | Reset metrics via test call                  |
| `make lint`             | Format all code using `black`                |
| `make dev-install`      | Recreate venv and reinstall dev dependencies |
| `make check`            | Re-run environment checks (docker, ollama)   |
| `make simulate`         | Simulate LLM traffic                         |
| `make smoke-test`       | Run simple `/llm` test                       |
| `make test-unit`        | Run only unit tests                          |
| `make test-e2e`         | Run only e2e tests                           |
| `make test`             | Run all tests (unit + e2e)                   |

> ℹ️ `make check` confirms `docker`, `sqlite3`, `.env`, `ollama`, and local model readiness.

---

## Pre-Commit Checklist

Before submitting a PR:

* [ ] Run `make test` (all tests must pass)
* [ ] Add test coverage for any new logic
* [ ] Run `make lint` to auto-format
* [ ] Validate `.env` usage if working with secrets
* [ ] Keep contributions modular and self-contained

---

## Commit Guidelines

We use [Conventional Commits](https://www.conventionalcommits.org/en/v1.0.0/):

```
feat(metrics): add histogram for token latency
fix(router): handle empty payload edge case
docs(contrib): clarify JWT setup in Makefile
```

---

## JWT Secrets (for E2E)

JWT is required for protected routes.
`make init` ensures `.env` exists, and `make generate-jwt` uses its value.

You can override `.env` using exported variables:

```bash
export JWT_SECRET=my-secret
make generate-jwt
```

Tests will fail early if `JWT_SECRET` is missing.

---

## Additional Docs

* [`README.md`](../README.md) — Product overview
* [`README.dev.md.`](../README.dev.md) — Developer setup and commands
* [`HOWTO_and_E2E_Testing.md`](./HOWTO_and_E2E_Testing.md) — Full workflow reference
---

Welcome aboard, we’re building this stack for real-world LLM ops at scale.
Every contribution improves visibility, velocity, and trust.

---
