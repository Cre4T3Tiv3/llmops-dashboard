"""
database.py

Lightweight SQLite-based logging module for LLMOps usage data.

Responsibilities:
    - Ensures `usage_logs` table exists before reads/writes.
    - Logs model prompt usage via `log_usage`.
    - Supports querying logs via:
        - `get_recent_logs(limit)`
        - `get_usage_by_model(model)`
        - `get_usage_by_client(user)`

Environment Variables:
    LLMOPS_DB_PATH: Path override for the SQLite database file. Defaults to "data/usage.db".
"""

import os
import sqlite3
from datetime import datetime, timezone
from functools import lru_cache
from typing import Dict, List

# Ensure data directory exists (default path)
os.makedirs("data", exist_ok=True)


@lru_cache()
def get_db_path() -> str:
    """
    Retrieve the SQLite database path, allowing for environment overrides.

    Returns:
        str: The resolved database file path.
    """
    return os.environ.get("LLMOPS_DB_PATH", "data/usage.db")


def ensure_table_exists():
    """
    Creates the `usage_logs` table if it doesn't already exist.

    This is a defensive check called before all database operations.
    """
    conn = sqlite3.connect(get_db_path())
    cursor = conn.cursor()
    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS usage_logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp TEXT,
            user TEXT,
            prompt TEXT,
            model TEXT,
            latency REAL,
            tokens INTEGER
        )
    """
    )
    conn.commit()
    conn.close()


def log_usage(user: str, prompt: str, model: str, latency: float, tokens: int):
    """
    Record a usage log entry for a prompt handled by an LLM.

    Args:
        user (str): The user ID submitting the prompt.
        prompt (str): The original prompt text.
        model (str): The name of the model used.
        latency (float): Inference duration in seconds.
        tokens (int): Token count of the prompt.

    Returns:
        None
    """
    ensure_table_exists()
    conn = sqlite3.connect(get_db_path())
    cursor = conn.cursor()
    cursor.execute(
        """
        INSERT INTO usage_logs (timestamp, user, prompt, model, latency, tokens)
        VALUES (?, ?, ?, ?, ?, ?)
        """,
        (
            datetime.now(timezone.utc).isoformat(),
            user,
            prompt,
            model,
            latency,
            tokens,
        ),
    )
    conn.commit()
    conn.close()


def get_recent_logs(limit: int = 10) -> List[Dict]:
    """
    Fetch the most recent LLM usage logs.

    Args:
        limit (int): Number of recent entries to return (default: 10).

    Returns:
        List[Dict]: List of log entries sorted by newest first.
    """
    ensure_table_exists()
    conn = sqlite3.connect(get_db_path())
    cursor = conn.cursor()
    cursor.execute(
        """
        SELECT id, timestamp, user, model, latency, tokens
        FROM usage_logs
        ORDER BY id DESC
        LIMIT ?
        """,
        (limit,),
    )
    rows = cursor.fetchall()
    conn.close()
    return [
        {
            "id": row[0],
            "timestamp": row[1],
            "user": row[2],
            "model": row[3],
            "latency": row[4],
            "tokens": row[5],
        }
        for row in rows
    ]


def get_usage_by_model(model: str) -> List[Dict]:
    """
    Fetch all log entries for a specific model.

    Args:
        model (str): Model name to filter logs by.

    Returns:
        List[Dict]: All log entries for the specified model.
    """
    ensure_table_exists()
    conn = sqlite3.connect(get_db_path())
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM usage_logs WHERE model = ?", (model,))
    rows = cursor.fetchall()
    conn.close()
    return [
        dict(
            zip(
                ["id", "timestamp", "user", "prompt", "model", "latency", "tokens"],
                row,
            )
        )
        for row in rows
    ]


def get_usage_by_client(user: str) -> List[Dict]:
    """
    Fetch all log entries submitted by a specific user/client.

    Args:
        user (str): User/client identifier.

    Returns:
        List[Dict]: All log entries for the given user.
    """
    ensure_table_exists()
    conn = sqlite3.connect(get_db_path())
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM usage_logs WHERE user = ?", (user,))
    rows = cursor.fetchall()
    conn.close()
    return [
        dict(
            zip(
                ["id", "timestamp", "user", "prompt", "model", "latency", "tokens"],
                row,
            )
        )
        for row in rows
    ]
