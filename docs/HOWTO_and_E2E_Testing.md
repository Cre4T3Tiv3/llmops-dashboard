# HOWTO + E2E TESTING: LLMOps Dashboard

A full guide to setting up, simulating, and debugging your local **LLMOps Dashboard** — from FastAPI to Prometheus to Grafana.

> ℹ️ Powered by LLaMA 3 (via Ollama) for secure, local inference.

---

## FULL STACK SETUP (LOCAL)

### Step 0: Clone & Initialize

```bash
git clone https://github.com/Cre4T3Tiv3/llmops-dashboard.git
cd llmops-dashboard
make init
```

This does everything:

* ✅ Verifies system tools (`docker`, `sqlite3`, `ollama`, etc.) via `make check`
* ✅ Installs [uv](https://github.com/astral-sh/uv) if missing
* ✅ Sets up `.venv` and installs dev dependencies
* ✅ Creates `.env` from `.env.example` if not already present
* ✅ Confirms Ollama model is available and ready (`llama3`)

> ℹ️ Re-run `make check` anytime to validate environment setup

---

### Step 1: Launch the Full Stack

```bash
make up
```

Services:

| Service    | URL                                            |
| ---------- | ---------------------------------------------- |
| FastAPI    | [http://localhost:8000](http://localhost:8000) |
| Prometheus | [http://localhost:9090](http://localhost:9090) |
| Grafana    | [http://localhost:3000](http://localhost:3000) |

---

### Step 2: Generate a Demo JWT

```bash
make generate-jwt
```

Returns a valid token for user `demo-user`.

---

### Step 3: Test `/llm/echo` (LLaMA 3 Local Model)

```bash
curl -X POST http://localhost:8000/llm/echo \
 -H "Authorization: Bearer <your-jwt-token>" \
 -H "Content-Type: application/json" \
 -H "x-user-id: demo-user" \
 -d '{"prompt": "What is retrieval augmented generation?"}'
```

Response (from `llama3`):

```json
{"response": "[llama3] Answer to: What is retrieval augmented generation?"}
```

---

### Step 4: Test `/metrics`

Visit:

```bash
http://localhost:8000/metrics
```

Look for:

```
request_count_total{endpoint="/llm/echo",method="POST",user="demo-user"} 1
```

---

### Step 5: View in Prometheus

Open:

```
http://localhost:9090
```

Query:

```promql
sum by(user) (rate(request_count_total[1m]))
```

---

### Step 6: Load Grafana Dashboard

Grafana runs with **anonymous access enabled by default** using the following preset credentials (configured via `.env`):

```env
GRAFANA_ADMIN_USER=admin         # ⚠️ Used for initial dashboard provisioning and local testing only (ChangeMe)
GRAFANA_ADMIN_PASSWORD=llmops    # ⚠️ Used for initial dashboard provisioning and local testing only (ChangeMe)
GRAFANA_ALLOW_ANON=true          # ⚠️ Used for initial dashboard provisioning and local testing only (ChangeMe)
```

To view the prebuilt LLMOps dashboard:

1. Open Grafana:
   [http://localhost:3000](http://localhost:3000)

   * You may already be logged in anonymously
   * Or use: `admin / llmops` if prompted

2. Sidebar → “+” → **Import**

3. Upload or paste the path:

```bash
grafana/dashboards/llmops_overview.json
```

4. You’ll see:

* LLM requests per user
* Latency histograms
* Token usage trends

> ℹ️ If the panel is blank, toggle **Bar ↔ Stat** and Save.

> ℹ️ **Tip:** You can disable anonymous mode or change admin credentials in `.env` before deployment.

---

### Step 7: SQLite Debugging (Optional)

```bash
make shell
sqlite3 data/usage.db 'SELECT * FROM usage_logs ORDER BY id DESC LIMIT 5;'
```

---

### Step 8: Simulate LLM Traffic

```bash
make simulate
```

This sends 25 test `/llm` calls using `demo-user`. Prometheus and Grafana will reflect the traffic.

---

### Step 9: Run Full Smoke Test

```bash
make smoke-test
```

Validates:

* JWT generation
* FastAPI `/llm` route
* `/metrics` scraping
* DB insert

---

## E2E TESTING

### Basic Flow

Use an isolated test DB:

```bash
export LLMOPS_DB_PATH=/tmp/test_usage.db
pytest -m e2e
```

Or run all test types via:

```bash
make test         # Run all tests
make test-unit    # Only unit tests
make test-e2e     # Only E2E tests
```

---

### Traffic + MCP Policy

Check these:

| File                             | Description                                  |
| -------------------------------- | -------------------------------------------- |
| `test_llm_echo.py`               | Validates local Ollama model via `/llm/echo` |
| `test_llm_traffic_simulation.py` | Simulates latency + LLM usage tracking       |
| `test_llm_flow.py`               | Validates DB + metric integration            |
| `test_mcp_registry.py`           | Confirms model registry behavior             |
| `test_mcp_policy.py`             | Enforces policy on tokens / limits           |

> ℹ️ MCP, metrics, and DB logging are verified end-to-end.

---

### Real-Time Metrics

When running via `make up`, Prometheus will show live stats:

```
http://localhost:9090
```

And Grafana renders all LLM traffic via:

```
http://localhost:3000
```

---

### Docker Notes

Docker Compose handles:

* Env var loading via `.env`
* Port exposure:

| Service    | Port |
| ---------- | ---- |
| FastAPI    | 8000 |
| Prometheus | 9090 |
| Grafana    | 3000 |

---

## Reset Prometheus

```bash
make reset-prometheus
```

Then verify:

```bash
curl 'http://localhost:9090/api/v1/series?match[]=request_count_total'
```

---

## JWT Secret Setup

This project **requires** `JWT_SECRET` to be set via `.env`, environment variables, or secret injection.

```env
JWT_SECRET=supersecretkey    # ⚠️ For local testing only (ChangeMe)
```

Validated at runtime:

```python
JWT_SECRET = os.getenv("JWT_SECRET")
if not JWT_SECRET:
    raise RuntimeError("JWT_SECRET must be set")
```

---

## TROUBLESHOOTING

### ❌ 401 Unauthorized

* Missing or expired JWT
* `x-user-id` header omitted
* Use `make generate-jwt` again

### ❌ `/metrics` is Empty

* Hit `/llm/echo` once to trigger metric
* Visit: [http://localhost:9090/targets](http://localhost:9090/targets)

### ❌ Grafana is Blank

* Toggle Stat ↔ Bar chart
* Reimport dashboard JSON

### ❌ No DB Entries

```bash
sqlite3 data/usage.db 'SELECT COUNT(*) FROM usage_logs;'
```

Confirm token and headers were passed correctly.

---

## License

MIT © 2025 [@Cre4T3Tiv3](https://github.com/Cre4T3Tiv3)

---
