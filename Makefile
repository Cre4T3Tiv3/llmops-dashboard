# ───────────────────────────────────────────────
# 🚀 CONTAINER LIFECYCLE COMMANDS
# ───────────────────────────────────────────────

up:
	make check
	docker-compose -f docker/docker-compose.yaml up --build

down:
	docker-compose -f docker/docker-compose.yaml down -v --remove-orphans

clean:
	docker-compose -f docker/docker-compose.yaml down -v --remove-orphans
	docker volume prune -f
	docker network prune -f
	rm -rf __pycache__
	@if ! rm -rf data/*.db 2>/dev/null; then \
		echo "🔐 Attempting sudo delete for data/*.db"; \
		sudo rm -rf data/*.db; \
	fi

nuke:
	@echo "🔥 Full cleanup in progress..."
	docker-compose -f docker/docker-compose.yaml down -v --remove-orphans || true
	docker system prune -a --volumes -f
	@echo "🛉 Removing cached build artifacts..."
	rm -rf __pycache__
	sudo rm -rf data/*.db || true
	sudo rm -rf prometheus-data || true
	@echo "✅ All containers, volumes, and caches removed. Rebuild with 'make up'"


# ───────────────────────────────────────────────
# 🔧 DEVELOPMENT + DEBUGGING UTILITIES
# ───────────────────────────────────────────────

logs:
	docker logs -f llmops-api

shell:
	docker exec -it llmops-api /bin/bash

generate-jwt:
	@python3 -c "import jwt, datetime; print(jwt.encode({'sub': 'demo-user', 'exp': datetime.datetime.utcnow() + datetime.timedelta(minutes=5)}, 'supersecretkey', algorithm='HS256'))" > .jwt.tmp && tail -n 1 .jwt.tmp

reset-prometheus:
	bash scripts/reset_prometheus_data.sh

check:
	@echo "🔍 Running system checks..."
	@command -v docker >/dev/null || (echo "❌ Docker not found" && exit 1)
	@command -v docker-compose >/dev/null || (echo "❌ docker-compose not found" && exit 1)
	@command -v sqlite3 >/dev/null || echo "⚠️ sqlite3 not found. Required for DB inspection during make smoke-test"
	@echo "✅ All required tools present"


# ───────────────────────────────────────────────
# ✅ TEST + TRAFFIC GENERATION
# ───────────────────────────────────────────────

simulate:
	bash ./scripts/simulate_llm_traffic.sh

smoke-test:
	bash ./scripts/smoke_test.sh

# ───────────────────────────────────────────────
# 📌 README USAGE NOTES
# ───────────────────────────────────────────────
# make simulate     → generates traffic for Grafana via demo-user
# make smoke-test   → runs E2E test of JWT, /llm, /metrics, and SQLite
