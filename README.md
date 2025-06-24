<p align="center">
  <a href="https://github.com/Cre4T3Tiv3/llmops-dashboard" target="_blank">
    <img src="https://raw.githubusercontent.com/Cre4T3Tiv3/llmops-dashboard/main/docs/assets/llmops_dashboard_v0.2.0.jpeg" alt="LLMOps Dashboard social preview" width="640"/>
  </a>
</p>

<p align="center">
  <em>Secure, observable, local-first LLM workflows that are powered by FastAPI, LLaMA3, and Prometheus</em>
</p>

<p align="center">
  <a href="https://github.com/Cre4T3Tiv3/llmops-dashboard/actions/workflows/ci.yml?query=branch%3Amain" target="_blank">
    <img src="https://github.com/Cre4T3Tiv3/llmops-dashboard/actions/workflows/ci.yml/badge.svg?branch=main" alt="CI">
  </a>
  <a href="https://www.python.org/downloads/" target="_blank">
    <img src="https://img.shields.io/badge/python-3.11+-blue.svg" alt="Python 3.11+">
  </a>
  <a href="https://opensource.org/licenses/MIT" target="_blank">
    <img src="https://img.shields.io/github/license/Cre4T3Tiv3/llmops-dashboard" alt="License: MIT">
  </a>
  <a href="https://github.com/Cre4T3Tiv3/llmops-dashboard/stargazers" target="_blank">
    <img src="https://img.shields.io/github/stars/Cre4T3Tiv3/llmops-dashboard?style=social" alt="GitHub Stars">
  </a>
  <a href="#contributing" target="_blank">
    <img src="https://img.shields.io/badge/contributions-welcome-brightgreen.svg" alt="Contributions welcome">
  </a>
</p>

## Why This Exists

LLMOps Dashboard is a modular open-source observability stack
for LLM systems that is built with FastAPI, Prometheus, Grafana, and SQLite.

It helps you monitor:

* Prompt/response metadata
* Latency (p95, per-user)
* Token usage and fallback behavior
* JWT-based user tracking
* Real-time dashboards for analysis

This OSS project provides a full-stack **starter template** for building
**production-grade observability for LLM applications** — local or cloud.

> ℹ️ Built for local-first development, extensibility, and minimal infra overhead.

---

## Model Control Plane (MCP)

The MCP (Model Control Plane) is a lightweight module that tracks **which models are used**, by **whom**, and under **what policy constraints**.

It enables:

| Capability                | Description                                                               |
| ------------------------- | ------------------------------------------------------------------------- |
| Model Registration     | Track models by name, size, alias, and source                             |
| Per-Client Policies    | Enforce token limits per user/client                                      |
| Dynamic Policy Control | Policies can be modified at runtime or pre-configured at boot             |
| Metrics Integration    | Token counts and usage policies propagate into `/metrics` Prometheus feed |
| Identity Tracking      | Associates JWT-authenticated users with tracked model usage               |

Example usage:

```python
from llmops.mcp import model_registry, usage_policy

# Register a model
model_registry.register_model("llama3", "8b", alias="dev")

# Apply a per-user token limit
usage_policy.set_policy("client-x", max_tokens=5000)
```

> ℹ️ This system can evolve into a **policy enforcement and audit framework**, especially in multi-user environments where tracking LLM usage, enforcing limits, or billing per token becomes critical.

---

## What It Does (Current Stack)

| Feature                 | Description                                             |
| ----------------------- | ------------------------------------------------------- |
| JWT Auth             | Secure `/llm` with per-user access tokens               |
| MCP Integration      | Tracks model usage, policy limits, token stats          |
| Prometheus Metrics   | Request rate, p95 latency, fallback %, etc.             |
| Grafana Dashboard    | Includes working starter panels for request and latency |
| SQLite Audit Trail   | Logs prompt, user, model, token count                   |
| Simulation + Testing | Run `make simulate` or `make smoke-test`                |
| LLM Integration     | Supports mock + real LLaMA 3 (Ollama) model endpoints    |
| LLaMA 3 (Ollama)    | Real local inference via `/llm/echo` using Ollama        |

## LLM Integration Status

This project supports **both mock and real LLM inference**:

### `/llm` (Simulated)

Default route for testing:

- Returns mock responses instantly
- Used for simulating traffic and testing fallback logic
- No network or real model required

```python
# Simulate fallback model logic
model_used = "openai-gpt"
if random.random() < 0.3:
    model_used = "local-ollama"
return {"response": f"[{model_used.capitalize()}] Answer to: {prompt}"}
````

### `/llm/echo` (Real LLaMA 3 via Ollama)

Backed by real local inference using [Ollama](https://ollama.com):

```bash
ollama run llama3
```

Once pulled, the model runs **offline** and is used for actual inference.

To call:

```bash
curl -X POST http://localhost:8000/llm/echo \
 -H "Authorization: Bearer <your-jwt>" \
 -H "x-user-id: demo-user" \
 -H "Content-Type: application/json" \
 -d '{"prompt": "What is vector search?"}'
```
---

## Planned Integrations (Roadmap)

Currently supported:

* ✅ Local LLM echo endpoint via `llama3` + Ollama (`/llm/echo`)
* ✅ GPU-ready Docker support with offline model warmup
* ✅ Prometheus + Grafana instrumentation
* ✅ Secure JWT-authenticated observability for LLM events
* ✅ SQLite-based request logging
* ✅ Test coverage and E2E support

Coming soon:

* [ ] Auto Summary Mode
  - Nightly background task summarizes recent logs via LLM
  - Stored in DB or JSON for display in Grafana summary panel

* [ ] Copilot UI Widget
  - Frontend prompt box sends input to `/llm`
  - Response is streamed or displayed with built-in observability

* [ ] Runtime LLM backend toggle (OpenAI, Ollama, HF)
* [ ] OAuth / Auth0 provider support
* [ ] Token pricing and billing estimation
* [ ] Slack alerting or LLM log summaries

Pluggable LLM Providers:

* [ ] OpenAI API via `openai.ChatCompletion`
* [x] Local Ollama models via `ollama run`
* [ ] Hugging Face `transformers` with local inference engine

> ℹ️ Contributions welcome — especially around modular LLM adapters and frontend UX.

---

## JWT Secrets

This project **requires** `JWT_SECRET` to be set via `.env`, environment variables, or secret injection.

```env
JWT_SECRET=supersecretkey        # ⚠️ For local testing only (ChangeMe)
```

### Used in code

```python
# token_issuer.py / auth.py
JWT_SECRET = os.getenv("JWT_SECRET")
if not JWT_SECRET:
    raise RuntimeError("JWT_SECRET must be set")
```

### Used in tests

```python
# conftest.py
secret = os.getenv("JWT_SECRET")
if not secret:
    raise RuntimeError("❌ JWT_SECRET not set in environment")
```

`.env` is auto-loaded in local development and test runs.
Docker services consume `JWT_SECRET` via `docker-compose.yaml`.

> ⚠️ Before production use, replace with secure injection methods:
>
> * Docker secrets
> * CI/CD secret management
> * Vault-backed key providers

---

## Grafana Access

By default, the dashboard uses:

```env
GRAFANA_ADMIN_USER=admin         # ⚠️ Used for initial dashboard provisioning and local testing only (ChangeMe)
GRAFANA_ADMIN_PASSWORD=llmops    # ⚠️ Used for initial dashboard provisioning and local testing only (ChangeMe)
GRAFANA_ALLOW_ANON=true          # ⚠️ Used for initial dashboard provisioning and local testing only (ChangeMe)
```

⚠️ Change these in `.env` for production deployments.

You can also enable or disable anonymous access via Grafana's `provisioning` config.

---

## Grafana Overview Dashboard

`grafana/dashboards/llmops_overview.json` includes:

| Panel Title                 | Description                           |
| --------------------------- | ------------------------------------- |
| LLM Request Rate by User | Frequency of requests per unique user |
| Latency by User (p95)    | p95 latency distribution by user ID   |

> ℹ️ Auto-loaded by Grafana on container start using provisioning config.
> ℹ️ Anonymous access enabled via `.env.example` credentials.

More panels (e.g., fallback %, token bar charts) can be added easily.

---

## Run Tests (Unit + E2E)

```bash
make test-unit     # Fast logic tests (auth, db, policy)
make test-e2e      # Full-stack smoke test w/ JWT and DB
```

> ℹ️ E2E tests simulate real API calls via HTTP, JWT, and DB assertions.

---

##  Quickstart

```bash
git clone https://github.com/Cre4T3Tiv3/llmops-dashboard.git
cd llmops-dashboard
make init
```

This does everything:

* Verifies required tools (`docker`, `sqlite3`, `ollama`, etc.) via `make check`
* Installs [uv](https://github.com/astral-sh/uv) if missing
* Sets up `.venv` and installs `pyproject.toml` dependencies
* Auto-creates `.env` from `.env.example` if missing
* Confirms your selected Ollama model (e.g. `llama3`) is available locally

This project uses [`uv`](https://github.com/astral-sh/uv) — a **fast and modern Python package manager** — for all local and Docker-based dependency management.

> ℹ️ No `requirements.txt` is needed — dependencies are resolved via `pyproject.toml`.

---

### Step 1: Verify Local Environment

Run the following to re-check your setup at any time:

```bash
make check
```

This confirms:

* Docker and docker-compose are available
* `sqlite3` is installed (required for `make smoke-test`)
* `.env` is present and contains necessary keys like `JWT_SECRET`
* `ollama` CLI is installed and working
* Your selected model (via `$OLLAMA_MODEL`) is installed

If the model is missing, you’ll see a warning like:

```bash
❌ Model 'llama3' not found in ollama list
```

> ℹ️ This step is included in `make init` but can be run independently.

---

### Step 2: Launch the Full Stack

```bash
make up
```

This builds and starts:

| Service    | URL                                            |
| ---------- | ---------------------------------------------- |
| FastAPI    | [http://localhost:8000](http://localhost:8000) |
| Prometheus | [http://localhost:9090](http://localhost:9090) |
| Grafana    | [http://localhost:3000](http://localhost:3000) |

> ℹ️ Dashboard at Grafana auto-loads `grafana/dashboards/llmops_overview.json`

---

### Want more? See:

[HOWTO and E2E Testing Guide](docs/HOWTO_and_E2E_Testing.md)
[Contributor Guide](docs/CONTRIBUTING.md)

---

## Sample Authenticated Request

```bash
make generate-jwt
curl -X POST http://localhost:8000/llm \
  -H "Authorization: Bearer <token>" \
  -H "x-user-id: demo-user" \
  -H "Content-Type: application/json" \
  -d '{"prompt": "What is RAG?"}'
```

---

## Directory Layout
```text
llmops-dashboard/
├── .dockerignore
├── .env
├── .env.example
├── .github/
│   └── workflows/
│       └── ci.yml
├── .gitignore
├── .jwt.tmp
├── Dockerfile
├── LICENSE
├── Makefile
├── README.dev.md
├── README.md
├── data/
├── docker-compose.override.yml
├── docker-compose.yaml
├── docs/
│   ├── CONTRIBUTING.md
│   └── HOWTO_and_E2E_Testing.md
├── grafana/
│   ├── dashboards/
│   │   └── llmops_overview.json
│   └── provisioning/
│       └── dashboards/
│           └── dashboards.yaml
├── llmops/
│   ├── auth.py
│   ├── database.py
│   ├── main.py
│   └── mcp/
│   │   ├── __init__.py
│   │   ├── client_tracker.py
│   │   ├── model_registry.py
│   │   └── usage_policy.py
│   └── routes/
│       ├── llm_echo.py
│       ├── llm_proxy.py
│       └── token_issuer.py
├── llmops_dashboard.egg-info/
├── prometheus.yml
├── pyproject.toml
└── tests/
    ├── conftest.py
    ├── e2e/
    │   ├── __init__.py
    │   ├── test_llm_echo.py
    │   ├── test_llm_flow.py
    │   ├── test_llm_traffic_simulation.py
    │   ├── test_metrics_exposure.py
    │   └── test_smoke_flow.py
    └── unit/
        ├── __init__.py
        ├── test_database.py
        ├── test_mcp_policy.py
        ├── test_mcp_registry.py
        ├── test_mcp_tracker.py
        └── test_reset_prometheus.py
```
---

## Makefile Commands

```bash
make up                # Start full stack (FastAPI + Prometheus + Grafana)
make generate-jwt      # Create test JWT
make simulate          # Send mock traffic to /llm
make smoke-test        # Full E2E: token → API → DB → metrics
make reset-prometheus  # Clean and rebuild metrics store
make clean             # Delete usage.db and logs
make nuke              # Destroy all containers, volumes, cache
```

> ℹ️ All commands assume `uv` is installed locally. See [uv GitHub page](https://github.com/astral-sh/uv)


### Want more? See:

[HOWTO and E2E Testing Guide](docs/HOWTO_and_E2E_Testing.md)
[Contributor Guide](docs/CONTRIBUTING.md)

---

## Requirements

* Docker (v20+)
* Linux or WSL (native Windows not supported yet)
* Python ≥ 3.10 for CLI/test scripts (optional)
* [`uv`](https://github.com/astral-sh/uv) for local development and installs

---

## Use Cases

* OpenAI/Ollama observability for internal tools
* Fine-grained request tracking (JWT, latency, token use)
* Test model fallback logic or simulate production LLM traffic
* Plug into billing or cost-monitoring with token metadata

---

## Built With

* [FastAPI](https://fastapi.tiangolo.com)
* [Prometheus](https://prometheus.io)
* [Grafana](https://grafana.com)
* [SQLite](https://www.sqlite.org/index.html)
* [Docker](https://www.docker.com)
* [uv](https://github.com/astral-sh/uv)

---

## Philosophy

This project isn’t just a toy but, it’s also not a locked-in framework.

You can:

* Swap SQLite for Postgres
* Swap Prometheus for OpenTelemetry
* Swap FastAPI for Flask or Django
* Swap JWT with OAuth or session-based auth

The patterns are here.
The rest is yours to extend ♻️

---

## License

[`MIT`](./LICENSE) – © 2025 [@Cre4T3Tiv3](https://github.com/Cre4T3Tiv3)

---

> Built for the LLM observability era.
> OSS, modular, and easy to reason about.

---
