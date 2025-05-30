# 🛠️ LLMOps Dashboard — Developer Notes

This document extends [`README.md`](./README.md) with advanced setup, debugging, and testing workflows tailored for contributors and maintainers.

---

## 🚀 Developer Quickstart

```bash
make init            # Verify tools, set up .venv, install deps
make up              # Launch full stack: FastAPI, Prometheus, Grafana
make generate-jwt    # Create demo JWT for user `demo-user`
make simulate        # Send traffic to /llm for metric generation
make logs            # Stream FastAPI logs
make shell           # Bash into FastAPI container
```

> 📘 See [CONTRIBUTING.md](docs/CONTRIBUTING.md) for PR conventions and coding standards.

---

## ✅ Environment Verifier (`make check`)

Run this anytime to confirm your machine is ready for development:

```bash
make check
```

This verifies:

* ✅ Docker and docker-compose availability
* ✅ `sqlite3` is installed (needed for DB and smoke tests)
* ✅ `.env` file exists and has `JWT_SECRET`
* ✅ `ollama` is installed and accessible
* ✅ The configured model (via `$OLLAMA_MODEL`, e.g., `llama3`) is present

If the model is missing, you’ll see:

```bash
❌ Model 'llama3' not found in ollama list
```

> This is automatically run as part of `make init`.

---

## 🔐 JWT Auth Debugging

```bash
make generate-jwt
```

Use the token in:

```bash
curl -X POST http://localhost:8000/llm \
  -H "Authorization: Bearer <token>" \
  -H "x-user-id: demo-user" \
  -H "Content-Type: application/json" \
  -d '{"prompt": "Explain embeddings"}'
```

* Token is signed with `JWT_SECRET` from `.env`
* Default subject is `demo-user`
* Valid for 5–15 minutes (see `token_issuer.py`)

> 🧪 Also used in tests (see `conftest.py` for validation)

---

## 📊 Grafana Dashboard Tips

### ✅ Default Dashboard Provisioning

This project auto-loads `grafana/dashboards/llmops_overview.json`
on container start via built-in provisioning (see `docker/grafana.ini`).

* Credentials & anonymous access controlled via `.env`

```env
GRAFANA_ADMIN_USER=admin         # ⚠️ Used for initial dashboard provisioning and local testing only (ChangeMe)
GRAFANA_ADMIN_PASSWORD=llmops    # ⚠️ Used for initial dashboard provisioning and local testing only (ChangeMe)
GRAFANA_ALLOW_ANON=true          # ⚠️ Used for initial dashboard provisioning and local testing only (ChangeMe)
  ```

* Access at [http://localhost:3000](http://localhost:3000)

### 🔁 If panels look empty:

* Change visualization type (e.g., Bar → Stat → Bar)
* Click “Save dashboard” to reload panel bindings

### 📤 Save custom dashboards:

1. Open dashboard → ⚙️ → JSON Model
2. Save to:

```bash
grafana/dashboards/llmops_overview.json
```

> Avoid hardcoding tokens, passwords, or local paths.

---

## 🔄 Reset Prometheus Metrics

```bash
make reset-prometheus
```

* Runs test to reset Prometheus state
* Volume will be reset if permissions allow

If access fails:

```bash
sudo chmod -R u+w prometheus-data/
```

---

## 🗃️ SQLite Debugging

Main DB is located at:

```bash
data/usage.db
```

Inspect logs:

```bash
sqlite3 data/usage.db 'SELECT * FROM usage_logs ORDER BY id DESC LIMIT 5;'
```

To wipe DB:

```bash
make clean
```

---

## 🧪 Testing + Simulation

| Command           | Description                                       |
| ----------------- | ------------------------------------------------- |
| `make simulate`   | Sends 25 `/llm` requests (triggers observability) |
| `make smoke-test` | Runs E2E: JWT, prompt, metrics, DB log            |
| `make test`       | All tests (unit + E2E + MCP)                      |

> 🔬 See [HOWTO\_and\_E2E\_Testing.md](docs/HOWTO_and_E2E_Testing.md) for walkthroughs.

---

## 🔥 Full Environment Reset

```bash
make nuke
```

Fully wipes your environment:

* Removes Docker containers, images, volumes
* Clears `prometheus-data` and `data/*.db`
* Deletes `.venv` and Python caches

> 🧹 To uninstall SQLite:
>
> * `sudo apt remove sqlite3`
> * `sudo dnf remove sqlite`
> * `sudo pacman -R sqlite`

---

## 📦 Dependency Management via `uv`

This project uses [`uv`](https://github.com/astral-sh/uv):

```bash
make dev-install
```

* Creates `.venv`
* Installs from `pyproject.toml` (no `requirements.txt`)
* Includes `[dev]` extras: `pytest`, `black`, etc.

---

## 🧪 MCP Test Coverage

| Module              | Responsibilities                       |
| ------------------- | -------------------------------------- |
| `model_registry.py` | Model ID tracking, timestamps          |
| `usage_policy.py`   | Token enforcement and per-user limits  |
| `client_tracker.py` | Request counts, latency aggregation    |
| `database.py`       | Full audit logs: prompt, tokens, model |

Run individual tests:

```bash
pytest tests/unit/test_database.py
pytest tests/e2e/test_smoke_flow.py
```

---

## 📁 Component Map

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

## ⚠️ Common Issues

| Problem                 | Fix                                 |
| ----------------------- | ----------------------------------- |
| `permission denied`     | `sudo chmod -R u+w data/`           |
| Grafana panels blank    | Change viz → Save dashboard         |
| Prometheus not scraping | Confirm `prometheus.yml` + mounts   |
| JWT not working         | Regenerate with `make generate-jwt` |
| Logs not showing        | Check headers, JWT, and `usage.db`  |
| Ollama error on /llm    | Run `ollama list`, ensure model     |

---

## 🧠 Roadmap Ideas

* ✅ Local LLaMA 3 echo integration via `/llm/echo`
* ✅ Ollama model warm-up + blob validation
* ✅ JWT-secured metrics + prompt logging
* 🧠 Auto Summary via scheduled script (summarize_logs.py)
* 🧠 Minimalist Copilot prompt box (auth + LLM streaming)
* 📈 Prometheus alert rules for latency, failures
* 🧩 Loki for centralized log ingestion
* ⚙️ Runtime backend toggle (Ollama/OpenAI/HF)
* 📋 Prompt history + stats table in Grafana

> Use these features to test local dev, CI observability, and future agentic workflows.

---

## 📜 License

MIT — see [`LICENSE`](./LICENSE)

---

Welcome to the observability edge for LLMOps. 🧠📈
Now go build responsibly.

---