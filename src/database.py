"""
database.py

This module provides lightweight usage tracking and retrieval via SQLite.

It is responsible for:
- Initializing the `usage_logs` table (if it doesn't exist).
- Inserting LLM request metadata into the database via `log_usage()`.
- Retrieving recent logs for inspection or dashboard purposes via `get_recent_logs()`.

Database: `data/usage.db`
"""

import sqlite3
from datetime import datetime
from typing import List, Dict

# Path to the local SQLite database
DB_PATH = "data/usage.db"

# Initialize database and ensure table exists
conn = sqlite3.connect(DB_PATH)
cursor = conn.cursor()
cursor.execute('''
    CREATE TABLE IF NOT EXISTS usage_logs (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        timestamp TEXT,
        user TEXT,
        prompt TEXT,
        model TEXT,
        latency REAL,
        tokens INTEGER
    )
''')
conn.commit()
conn.close()

def log_usage(user: str, prompt: str, model: str, latency: float, tokens: int):
    """
    Inserts a new usage log entry into the database.

    Args:
        user (str): Identifier for the user making the request.
        prompt (str): The text prompt submitted to the model.
        model (str): The model that handled the request (e.g., "openai-gpt").
        latency (float): Time taken (in seconds) to generate a response.
        tokens (int): Number of tokens processed in the prompt.
    """
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO usage_logs (timestamp, user, prompt, model, latency, tokens)
        VALUES (?, ?, ?, ?, ?, ?)
    ''', (datetime.utcnow().isoformat(), user, prompt, model, latency, tokens))
    conn.commit()
    conn.close()

def get_recent_logs(limit: int = 10) -> List[Dict]:
    """
    Retrieves the most recent usage logs.

    Args:
        limit (int): Number of recent entries to retrieve (default is 10).

    Returns:
        List[Dict]: A list of usage log entries sorted by most recent.
    """
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute('''
        SELECT id, timestamp, user, model, latency, tokens
        FROM usage_logs
        ORDER BY id DESC
        LIMIT ?
    ''', (limit,))
    rows = cursor.fetchall()
    conn.close()
    return [
        {
            "id": row[0],
            "timestamp": row[1],
            "user": row[2],
            "model": row[3],
            "latency": row[4],
            "tokens": row[5]
        }
        for row in rows
    ]
