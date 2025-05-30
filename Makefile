# ✅ AUTOLOAD .env IF PRESENT
ifneq (,$(wildcard .env))
    include .env
    export
endif

init:
	@echo "🛠️  Initializing development environment..."
	@$(MAKE) check
	@if ! command -v uv >/dev/null 2>&1; then \
		echo "🚧 'uv' not found. Installing..."; \
		curl -Ls https://astral.sh/uv/install.sh | sh; \
	else \
		echo "✅ uv already installed."; \
	fi
	@echo "📦 Creating virtual environment..."
	uv venv
	@echo "🔁 Installing project in editable mode with dev extras..."
	uv pip install -e .[dev]
	@echo "🔐 Setting up environment variables..."
	@if [ ! -f .env ]; then cp .env.example .env && echo '✅ .env created from .env.example'; else echo '⚠️  .env already exists. Skipping.'; fi
	@echo "✅ Environment initialized. Use 'make up' to run the stack."

# ─────────────────────────────
# 🚀 CONTAINER LIFECYCLE
# ─────────────────────────────

up:
	make check
	docker-compose -f ./docker-compose.yaml up --build

down:
	docker-compose -f ./docker-compose.yaml down -v --remove-orphans
clean:
	@echo "🧹 Stopping and removing containers, volumes, and networks..."
	docker-compose -f ./docker-compose.yaml down -v --remove-orphans

	@echo "🗑️ Pruning unused Docker volumes and networks..."
	docker volume prune -f
	docker network prune -f

	@echo "🧼 Removing dangling Docker images..."
	docker image prune -f

	@echo "🧽 Removing Python cache..."
	rm -rf __pycache__

	@echo "🗄️ Removing local SQLite DBs..."
	@if ! rm -rf data/*.db 2>/dev/null; then \
		echo "🔐 Attempting sudo delete for data/*.db"; \
		sudo rm -rf data/*.db; \
	fi

	@echo "🧼 Removing virtual environment..."
	rm -rf .venv

	@echo "🗒️ .env is preserved — remove manually if sensitive:"
	@echo "    rm .env"

	@echo "✅ Clean complete. To rebuild from scratch, run:"
	@echo "    make dev"

nuke:
	@echo "🔥 Full cleanup in progress..."
	docker-compose -f ./docker-compose.yaml down -v --remove-orphans || true
	docker system prune -a --volumes -f
	@echo "🛉 Removing cached build artifacts..."
	rm -rf __pycache__
	sudo rm -rf data/*.db || true
	sudo rm -rf prometheus-data || true
	@echo "✅ Rebuild with 'make up'"
	@echo "ℹ️  If you installed sqlite3 during setup, it remains a global dependency."
	@echo "   You can remove it manually via your package manager if desired:"
	@echo "     sudo apt-get remove sqlite3          # Debian/Ubuntu"
	@echo "     sudo dnf remove sqlite               # RedHat/Fedora"
	@echo "     sudo pacman -R sqlite                # Arch"

# ─────────────────────────────
# 🔧 DEV + DEBUG UTILITIES
# ─────────────────────────────

dev:
	docker-compose up --build

logs:
	docker logs -f llmops-api

shell:
	docker exec -it llmops-api /bin/bash

generate-jwt:
	@if [ -z "$$JWT_SECRET" ]; then \
		echo "❌ JWT_SECRET not set. Please define it in your .env file."; \
		exit 1; \
	fi
	@python3 -c "import jwt, datetime, os; \
print(jwt.encode({'sub': 'demo-user', 'exp': datetime.datetime.utcnow() + datetime.timedelta(minutes=5)}, os.getenv('JWT_SECRET'), algorithm='HS256'))" \
	> .jwt.tmp && tail -n 1 .jwt.tmp

reset-prometheus:
	pytest tests/unit/test_reset_prometheus.py

check:
	@echo "🔍 Running system checks..."

	@# ────────────────
	@# Docker + Compose
	@# ────────────────
	@command -v docker >/dev/null || (echo "❌ Docker not found" && exit 1)
	@command -v docker-compose >/dev/null || (echo "❌ docker-compose not found" && exit 1)
	@echo "✅ Docker + Compose available."

	@# ─────────────
	@# sqlite3 check
	@# ─────────────
	@if ! command -v sqlite3 >/dev/null; then \
		echo "⚠️  sqlite3 not found."; \
		read -p "❓ Install sqlite3 now? (y/N) " RESP; \
		if [ "$$RESP" = "y" ] || [ "$$RESP" = "Y" ]; then \
			if [ -f /etc/debian_version ]; then \
				echo "🔧 Installing via apt..."; \
				sudo apt-get update && sudo apt-get install -y sqlite3; \
			elif [ -f /etc/redhat-release ]; then \
				echo "🔧 Installing via dnf..."; \
				sudo dnf install -y sqlite; \
			elif [ -f /etc/arch-release ]; then \
				echo "🔧 Installing via pacman..."; \
				sudo pacman -Sy sqlite; \
			elif [ -f /etc/alpine-release ]; then \
				echo "🔧 Installing via apk..."; \
				sudo apk add sqlite; \
			else \
				echo "🚫 Auto-install not supported. Install manually."; \
			fi; \
			command -v sqlite3 >/dev/null && echo '✅ sqlite3 installed.' || echo '❌ Failed to install sqlite3.'; \
		else \
			echo "⚠️  Skipping. Some tests may fail without sqlite3."; \
		fi; \
	else \
		echo "✅ sqlite3 is available."; \
	fi

	@# ─────────────
	@# Ollama check
	@# ─────────────
	@if ! command -v ollama >/dev/null; then \
		echo "⚠️  Ollama not found."; \
		read -p "❓ Install Ollama now? (y/N) " RESP; \
		if [ "$$RESP" = "y" ] || [ "$$RESP" = "Y" ]; then \
			echo "🔧 Installing Ollama via install.sh..."; \
			curl -fsSL https://ollama.com/install.sh | sh; \
			command -v ollama >/dev/null && echo '✅ Ollama installed.' || echo '❌ Ollama install failed.'; \
		else \
			echo "⚠️  Skipping. LLM calls will fail."; \
		fi; \
	else \
		echo "✅ Ollama CLI is available."; \
	fi

	@# ────────────────────────────────
	@# Check model (default: llama3)
	@# ────────────────────────────────
	@MODEL=$$(grep OLLAMA_MODEL .env 2>/dev/null | cut -d '=' -f2 || echo "llama3"); \
	if curl -s http://localhost:11434/api/tags >/dev/null; then \
		if ! curl -s http://localhost:11434/api/tags | grep -q "$$MODEL"; then \
			read -p "⚠️  Ollama model '$$MODEL' not found. Pull now? (y/N) " RESP; \
			if [ "$$RESP" = "y" ] || [ "$$RESP" = "Y" ]; then \
				curl -s -X POST http://localhost:11434/api/pull -d "{\"name\": \"$$MODEL\"}" && \
				echo "✅ Model '$$MODEL' pulled successfully."; \
			else \
				echo "⚠️  Skipping. /llm/echo will fail without model."; \
			fi; \
		else \
			echo "✅ Ollama model '$$MODEL' is already available."; \
		fi; \
	else \
		echo "⚠️  Skipping model check — Ollama API not reachable."; \
	fi

# ─────────────────────────────
# ✅ TEST + TRAFFIC (E2E)
# ─────────────────────────────

simulate:
	pytest tests/e2e/test_llm_traffic_simulation.py

smoke-test:
	@echo "⏳ Waiting for FastAPI to become available..."
	@until curl -s http://localhost:8000 > /dev/null; do sleep 1; done
	@echo "✅ FastAPI is up. Running test..."
	pytest tests/e2e/test_smoke_flow.py

# ─────────────────────────────
# 🧪 TEST + LINT
# ─────────────────────────────

test:
	pytest

lint:
	black llmops tests

test-unit:
	pytest tests/unit

test-e2e:
	pytest tests/e2e

# ─────────────────────────────
# 📦 MODERN DEV INSTALL (UV)
# ─────────────────────────────
dev-install:
	uv venv
	uv pip install -e .[dev]
