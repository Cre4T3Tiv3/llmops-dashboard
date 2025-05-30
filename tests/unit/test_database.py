"""
test_database.py

Unit test for the LLMOps `database.py` module.

Verifies the ability to:
- Override database path using a temporary file
- Log a simulated LLM usage entry
- Fetch and assert the correct log content
"""

import os

import pytest

from llmops.database import get_db_path, get_recent_logs, log_usage


@pytest.mark.unit
def test_log_and_fetch(tmp_path):
    """
    Test logging and fetching usage logs with a temporary database.

    This test:
        - Overrides the database location using pytest's tmp_path
        - Clears any cached db path to force reload
        - Logs a mock LLM usage entry
        - Verifies that the logged model is found in retrieved logs

    Args:
        tmp_path (Path): pytest fixture providing a unique temporary directory.
    """
    # Override DB path using tmp_path
    test_db = tmp_path / "test_usage.db"
    os.environ["LLMOPS_DB_PATH"] = str(test_db)

    # Clear cached path to apply override
    get_db_path.cache_clear()

    # Log an example LLM usage entry
    log_usage("test_user", "Say something", "gpt-test", 0.123, 42)

    # Fetch recently logged usage entries
    logs = get_recent_logs()

    # Assert at least one log entry contains the expected model
    assert any(log["model"] == "gpt-test" for log in logs)
