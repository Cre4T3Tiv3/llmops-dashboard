"""
test_mcp_policy.py

Unit tests for the usage_policy module.

Verifies:
- Existence of the default usage policy in the global policy registry.
"""

import pytest

from llmops.mcp.usage_policy import USAGE_POLICIES


@pytest.mark.unit
def test_default_policy_exists():
    """
    Test to ensure that a 'default' usage policy is present.

    The default policy is required to apply fallback limits and restrictions
    for clients without custom-defined policies.

    Asserts:
        - The key "default" exists in the USAGE_POLICIES dictionary.
    """
    assert "default" in USAGE_POLICIES
