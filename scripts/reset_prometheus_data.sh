#!/usr/bin/env bash
# scripts/reset_prometheus_data.sh

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"
COMPOSE_FILE="$PROJECT_ROOT/docker/docker-compose.yaml"
PROM_SERVICE="prometheus"

echo "🧹 Stopping Prometheus container..."
docker-compose -f "$COMPOSE_FILE" --project-directory "$PROJECT_ROOT" stop "$PROM_SERVICE"

# Optional: Remove data if you use a local mount (adjust if needed)
PROM_DATA_DIR="$PROJECT_ROOT/docker/prometheus-data"
if [ -d "$PROM_DATA_DIR" ]; then
    echo "🗑️ Removing local Prometheus data at: $PROM_DATA_DIR"
    rm -rf "$PROM_DATA_DIR"
else
    echo "ℹ️ No local Prometheus data directory found to wipe."
fi

echo "🚀 Restarting Prometheus..."
docker-compose -f "$COMPOSE_FILE" --project-directory "$PROJECT_ROOT" up -d "$PROM_SERVICE"

echo "✅ Prometheus reset complete."
