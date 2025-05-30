"""
test_mcp_registry.py

Unit tests for the model_registry module.

Verifies:
- That models can be successfully registered into the MODEL_REGISTRY.
"""

import pytest

from llmops.mcp.model_registry import MODEL_REGISTRY, register_model


@pytest.mark.unit
def test_model_register():
    """
    Test that a model can be registered correctly.

    This test registers a model called "llama3" with version "8b"
    and alias "test", then verifies that "llama3" is present in
    the global MODEL_REGISTRY dictionary.

    Asserts:
        - The registered model name is present in MODEL_REGISTRY.
    """
    register_model("llama3", "8b", alias="test")
    assert "llama3" in MODEL_REGISTRY
