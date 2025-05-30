"""
usage_policy.py

Manages per-client usage policies for model access within the Model Control Plane (MCP).

This includes token usage limits and model-level blocklists.

Attributes:
    USAGE_POLICIES (dict): In-memory mapping of client IDs to their usage policy.
        Each policy includes:
            - max_tokens (int): Maximum allowed tokens for the client.
            - blocked_models (list): List of model names the client is restricted from using.
"""

USAGE_POLICIES = {"default": {"max_tokens": 100000, "blocked_models": []}}


def set_policy(client_id, max_tokens, blocked_models=None):
    """
    Sets or updates a usage policy for a given client.

    Args:
        client_id (str): Unique identifier of the client.
        max_tokens (int): Maximum tokens the client is allowed to use.
        blocked_models (list, optional): List of model names to block. Defaults to [].

    Returns:
        None
    """
    USAGE_POLICIES[client_id] = {
        "max_tokens": max_tokens,
        "blocked_models": blocked_models or [],
    }


def check_policy(client_id, model_name, token_count):
    """
    Validates whether a model usage request complies with the client's policy.

    Args:
        client_id (str): Unique identifier of the client.
        model_name (str): Name of the model being accessed.
        token_count (int): Number of tokens the request will consume.

    Returns:
        tuple:
            - bool: True if the request is allowed, False otherwise.
            - str: Reason for the decision ("Allowed", "Token limit exceeded", etc.)
    """
    policy = USAGE_POLICIES.get(client_id, USAGE_POLICIES["default"])
    if model_name in policy["blocked_models"]:
        return False, "Model is blocked"
    if token_count > policy["max_tokens"]:
        return False, "Token limit exceeded"
    return True, "Allowed"
