# 🛠️ LLMOps Dashboard — Developer Notes

This guide supplements the main `README.md` with internal setup instructions, Grafana tips, metrics reset logic, and debugging workflows for contributors and maintainers.

---

## 🧰 Developer Quickstart

```bash
make up             # Start full stack (FastAPI, Prometheus, Grafana)
make generate-jwt   # Create a demo JWT for testing
make simulate       # Send traffic to /llm for dashboard validation
make logs           # Tail FastAPI logs live
make shell          # Enter API container shell
```

---

## 🔐 JWT Auth Debugging

### Generate and Use a Token

```bash
make generate-jwt
```

Use the printed token with:

```bash
curl -X POST http://localhost:8000/llm \
  -H "Authorization: Bearer <token>" \
  -H "x-user-id: demo-user" \
  -H "Content-Type: application/json" \
  -d '{"prompt": "Explain embeddings"}'
```

* Token is signed with `JWT_SECRET` from `.env`
* Subject is always `demo-user` by default
* Expires in \~15 minutes (customizable in `token_issuer.py`)

---

## 🔄 Reset Prometheus Metrics

If dashboards become noisy or inflated due to simulation traffic:

```bash
make reset-prometheus
```

This performs:

* Stops the Prometheus container
* Deletes local volume (`prometheus-data/`)
* Rebuilds the container with fresh metrics

⚠️ **If permission denied**:

```bash
sudo chmod -R u+w prometheus-data/
```

---

## 📊 Grafana Dashboard Tips

### Reimporting or Refreshing

If panels show `No Data` even with valid traffic:

* Switch panel visualization type temporarily (e.g., `Bar` → `Stat`)
* Save the dashboard after reverting back
* This forces a refresh and resets internal data bindings

### Exporting Changes

After modifying dashboards:

1. Click the ⚙️ gear icon → "JSON Model"
2. Save into: `grafana/dashboards/llmops_overview.json`
3. Avoid saving any absolute paths or injected secrets

---

## 🗃️ SQLite Usage Logs

* Logs live in `data/usage.db`
* Contains: `user`, `prompt`, `model`, `latency`, and `tokens`

Example:

```bash
sqlite3 data/usage.db 'SELECT * FROM usage_logs ORDER BY id DESC LIMIT 5;'
```

To reset DB:

```bash
make clean
```

---

## 🧪 Testing Scripts

| Command           | Description                                    |
| ----------------- | ---------------------------------------------- |
| `make simulate`   | Sends 25 requests to `/llm` with `demo-user`   |
| `make smoke-test` | Full check of JWT, `/llm`, metrics, and SQLite |

---

## 🔥 Full Reset

To wipe **everything** (volumes, cache, DB, metrics):

```bash
make nuke
```

Removes:

* Containers
* All volumes (incl. Prometheus + SQLite)
* Cached Python/DB files

---

## 🧩 Component Map

```text
llmops-dashboard/
├── src/                  # FastAPI app
│   ├── main.py           # App entrypoint + middleware
│   ├── auth.py           # JWT verification logic
│   ├── database.py       # SQLite logging
│   └── routes/           # /llm and /auth handlers
├── grafana/              # Dashboards & persistent data
│   └── dashboards/
│       └── llmops_overview.json
├── docker/               # docker-compose + Prometheus config
│   └── prometheus.yml
├── scripts/              # Traffic simulator, smoke test, reset
├── data/                 # usage.db lives here (gitignored)
├── Makefile              # One-liner developer commands
└── .env / .env.example   # FastAPI secrets
```

---

## ⚠️ Common Gotchas

| Symptom                   | Fix                                                                |
| ------------------------- | ------------------------------------------------------------------ |
| `permission denied` on DB | `sudo chmod -R u+w data/`                                          |
| Grafana panel shows blank | Toggle viz type (e.g. Bar → Stat), then save                       |
| Prometheus fails to start | Check volume mount path vs. file (`prometheus.yml` must be a file) |
| JWT invalid or expired    | Re-run `make generate-jwt`                                         |
| SQLite not logging        | Ensure `/llm` is hit with valid headers + token                    |

---

## 🧠 Future Enhancements

* ✅ Add alert rules for spike detection (fallback %, latency, errors)
* 🔗 Hook into Loki / Elasticsearch for log aggregation
* 🔁 Use Ollama or OpenAI completions in `llm_proxy.py`
* 📋 Render recent prompts in Grafana using a table panel or exporter

---

## 🔒 Maintainer Notes

* Internal-only dashboards: `grafana/dashboards/dev_*.json`
* Public dashboards: `llmops_overview.json` only
* Never commit: `.env`, `data/*.db`, local token values

---

## 📜 License

MIT — see `LICENSE`

---