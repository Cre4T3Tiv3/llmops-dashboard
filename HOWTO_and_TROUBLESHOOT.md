# 🧪 HOWTO + TROUBLESHOOT: LLMOps Dashboard

A full guide to setting up, simulating, and debugging your local **LLMOps Dashboard** stack.

---

## 🔄 Reset Prometheus (Optional)

To start with a clean slate for metrics:

```bash
make reset-prometheus
```

To confirm:

```bash
curl 'http://localhost:9090/api/v1/series?match[]=request_count_total'
```

---

## ✅ FULL WALKTHROUGH: Run the LLMOps Stack Locally

### 🪜 Step 0: Clone + Prepare

```bash
git clone https://github.com/Cre4T3Tiv3/llmops-dashboard.git
cd llmops-dashboard
cp .env.example .env
```

---

### 🪜 Step 1: Start the Stack

```bash
make up
```

Verify services:

* 🧠 FastAPI: [http://localhost:8000](http://localhost:8000)
* 📈 Prometheus: [http://localhost:9090](http://localhost:9090)
* 📊 Grafana: [http://localhost:3000](http://localhost:3000)

Check:

```bash
docker ps
```

---

### 🪜 Step 2: Generate a Demo JWT

```bash
make generate-jwt
```

Output token is for user `demo-user`.

---

### 🪜 Step 3: Hit the `/llm` Endpoint

```bash
curl -X POST http://localhost:8000/llm \
 -H "Authorization: Bearer <your-jwt-token>" \
 -H "Content-Type: application/json" \
 -H "x-user-id: demo-user" \
 -d '{"prompt": "What is vector search?"}'
```

Example response:

```json
{"response": "[Openai-gpt] Answer to: What is vector search?"}
```

---

### 🪜 Step 4: View Metrics in Prometheus

```bash
http://localhost:8000/metrics
```

Should include:

```
request_count_total{endpoint="/llm",method="POST",user="demo-user"} 5
```

Try a query in Prometheus:

```promql
sum by(user) (rate(request_count_total{endpoint="/llm",method="POST"}[1m]))
```

---

### 🪜 Step 5: Import Grafana Dashboard

1. Visit [http://localhost:3000](http://localhost:3000)
2. Login: `admin / admin`
3. Sidebar → **+ → Import**
4. Upload `grafana/dashboards/llmops_overview.json`

You’ll see:

* 📈 LLM Request Rate by User
* 📉 Latency by User (p95)

> If stat panels show no data at first, edit → switch panel type (e.g., to Bar and back) → Save

---

### 🪜 Step 6 (Optional): Inspect SQLite Logs

```bash
make shell
sqlite3 data/usage.db 'SELECT * FROM usage_logs ORDER BY id DESC LIMIT 5;'
```

---

### 🪜 Step 7 (Optional): Simulate Dashboard Traffic

```bash
make simulate
```

Sends 25 LLM calls using `demo-user` — helpful for dashboards.

---

### 🪜 Step 8 (Optional): Run Full System Check

```bash
make smoke-test
```

Covers:

* JWT generation
* `/llm` call
* `/metrics` response
* SQLite insertion

---

## 🛠️ Helpful Commands

```bash
make up            # Start the stack
make logs          # Stream FastAPI logs
make shell         # Open shell in API container
make generate-jwt  # Generate demo JWT
make simulate      # Send traffic to /llm
make smoke-test    # E2E check (JWT, metrics, logs)
make clean         # Teardown + wipe DB, volumes
make reset-prometheus # Clean and restart Prometheus metrics
```

---

## 🚨 TROUBLESHOOTING

### ❌ `/llm` returns 401 or empty

* JWT may be expired or missing
* Ensure `x-user-id: demo-user` header is sent
* Logs: `make logs`

### ❌ `/metrics` is empty

* Call `/llm` at least once
* Check if Prometheus is scraping: [http://localhost:9090/targets](http://localhost:9090/targets)

### ❌ Grafana dashboard is blank

* Try re-importing JSON
* Switch stat panel type to Bar → Stat
* Confirm `uid: Prometheus` is selected in panel datasource

### ❌ SQLite logs missing

* Ensure `/llm` was hit with valid token
* Use:

```bash
sqlite3 data/usage.db 'SELECT COUNT(*) FROM usage_logs;'
```

---

## 📜 License

MIT — see `LICENSE`

---