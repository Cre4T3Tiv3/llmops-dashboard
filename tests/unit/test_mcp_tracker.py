"""
test_mcp_tracker.py

Unit test for the client_tracker module.

Verifies:
- That client usage can be logged.
- That statistics are accurately calculated per client.
"""

import pytest

from llmops.mcp.client_tracker import get_client_stats, log_client_usage


@pytest.mark.unit
def test_logging_and_stats():
    """
    Test that usage logging and stats calculation work.

    Logs token usage for a client ("abc") and retrieves their stats.
    Validates that the total token count reflects the logged value.

    Asserts:
        - 'total_tokens' is at least the logged token value.
    """
    log_client_usage("abc", "llama", 100)
    stats = get_client_stats("abc")
    assert stats["total_tokens"] >= 100
