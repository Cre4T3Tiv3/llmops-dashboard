"""
model_registry.py

Provides model registration and lookup utilities for the Model Control Plane (MCP).

This module tracks models by name, version, and alias, and persists them to disk.

Attributes:
    MODEL_REGISTRY (dict): An in-memory dictionary of registered models.
    MODEL_REGISTRY_FILE (str): Path to the JSON file for saving/loading the registry.
"""

import json
import os

MODEL_REGISTRY = {}
MODEL_REGISTRY_FILE = "data/model_registry.json"


def register_model(name, version, alias=None):
    """
    Registers a new model in the MCP registry.

    Args:
        name (str): Unique name of the model.
        version (str): Version tag or identifier of the model.
        alias (str, optional): Alternate name for the model. Defaults to `name`.

    Returns:
        None
    """
    MODEL_REGISTRY[name] = {"version": version, "alias": alias or name}


def get_model_info(name_or_alias):
    """
    Retrieves model information by name or alias.

    Args:
        name_or_alias (str): Model name or alias to search for.

    Returns:
        dict or None: Dictionary containing model metadata, or None if not found.
    """
    for name, info in MODEL_REGISTRY.items():
        if name == name_or_alias or info["alias"] == name_or_alias:
            return info
    return None


def save_registry():
    """
    Saves the current in-memory model registry to disk as JSON.

    Returns:
        None
    """
    with open(MODEL_REGISTRY_FILE, "w") as f:
        json.dump(MODEL_REGISTRY, f)


def load_registry():
    """
    Loads the model registry from disk into memory.

    Returns:
        None
    """
    global MODEL_REGISTRY
    if os.path.exists(MODEL_REGISTRY_FILE):
        with open(MODEL_REGISTRY_FILE, "r") as f:
            MODEL_REGISTRY = json.load(f)
