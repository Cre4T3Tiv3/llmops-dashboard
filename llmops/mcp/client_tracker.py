"""
client_tracker.py

Provides in-memory tracking for client usage of LLM models.

This module maintains a simple in-process log of token usage per client.
Useful for diagnostics, basic analytics, and debugging purposes in the MCP.

Attributes:
    CLIENT_LOGS (dict): A dictionary mapping client IDs to a list of usage entries.
"""

CLIENT_LOGS = {}


def log_client_usage(client_id, model_name, tokens_used):
    """
    Logs token usage for a specific client and model.

    Args:
        client_id (str): Unique identifier of the client/user.
        model_name (str): The name or alias of the LLM model used.
        tokens_used (int): Number of tokens consumed in the request.

    Returns:
        None
    """
    if client_id not in CLIENT_LOGS:
        CLIENT_LOGS[client_id] = []
    CLIENT_LOGS[client_id].append({"model": model_name, "tokens": tokens_used})


def get_client_summary(client_id):
    """
    Retrieves the full usage history for a specific client.

    Args:
        client_id (str): Unique identifier of the client/user.

    Returns:
        list[dict]: A list of usage entries containing model name and tokens used.
    """
    return CLIENT_LOGS.get(client_id, [])


def get_client_stats(client_id):
    """
    Computes usage statistics for a specific client.

    Args:
        client_id (str): Unique identifier of the client/user.

    Returns:
        dict: A dictionary with total token usage, request count, and average tokens per request.
    """
    usage = CLIENT_LOGS.get(client_id, [])
    if not usage:
        return {"total_tokens": 0, "request_count": 0, "avg_tokens": 0}
    total_tokens = sum(entry["tokens"] for entry in usage)
    count = len(usage)
    avg = total_tokens / count
    return {"total_tokens": total_tokens, "request_count": count, "avg_tokens": avg}
