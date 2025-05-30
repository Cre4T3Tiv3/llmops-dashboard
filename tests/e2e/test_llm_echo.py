"""
llm_proxy.py

Defines FastAPI routes for simulating LLM interactions and retrieving recent usage logs.

This module includes:
- POST /llm: Simulates an LLM (e.g., OpenAI or local model) response with mocked latency and token usage.
- POST /echo: Simple public test route that returns the original prompt string (used for smoke tests).
- GET /logs: Returns recent LLM usage logs with a configurable limit.

Used for testing LLM observability metrics, latency tracking, and usage history inspection.

Dependencies:
    - log_usage (llmops.database): Persists request metadata.
    - get_recent_logs (llmops.database): Retrieves usage logs for observability or UI display.
"""

import random
import time
from typing import List

from fastapi import APIRouter, Depends, Query, Request
from pydantic import BaseModel

from llmops.database import get_recent_logs, log_usage

router = APIRouter()


class PromptRequest(BaseModel):
    """
    Request schema for sending a prompt to the LLM.

    Attributes:
        prompt (str): Text string representing the user prompt sent to the LLM.
    """

    prompt: str


class PromptResponse(BaseModel):
    """
    Response schema for the LLM simulation result.

    Attributes:
        response (str): Generated response string (mocked for simulation).
    """

    response: str


@router.post("/llm", response_model=PromptResponse)
def call_llm(request: Request, body: PromptRequest) -> PromptResponse:
    """
    Simulates a call to a large language model and logs the request for monitoring.

    Includes fallback routing logic with randomized model switching and latency simulation.

    Args:
        request (Request): FastAPI request object containing headers like x-user-id.
        body (PromptRequest): JSON body containing the user prompt.

    Returns:
        PromptResponse: Simulated model response with attribution label.
    """
    prompt = body.prompt
    user = request.headers.get("x-user-id", "anonymous")

    start_time = time.time()

    # Simulated fallback routing: 30% chance to use local model
    model_used = "openai-gpt"
    if random.random() < 0.3:
        model_used = "local-ollama"

    latency = time.time() - start_time
    token_count = len(prompt.split())

    log_usage(
        user=user, prompt=prompt, model=model_used, latency=latency, tokens=token_count
    )

    return PromptResponse(response=f"[{model_used.capitalize()}] Answer to: {prompt}")


@router.get("/logs")
def fetch_logs(limit: int = Query(10, ge=1, le=100)) -> List[dict]:
    """
    Retrieves the N most recent LLM usage logs.

    Useful for dashboard views or debugging end-to-end request flows.

    Args:
        limit (int, optional): Number of logs to retrieve (1–100). Defaults to 10.

    Returns:
        List[dict]: Chronologically sorted usage logs from newest to oldest.
    """
    return get_recent_logs(limit=limit)


@router.post("/echo")
async def echo(prompt: dict):
    """
    Echoes back the prompt field from the request payload.

    This is a simple public test endpoint to validate API connectivity.

    Args:
        prompt (dict): JSON body with a 'prompt' key.

    Returns:
        dict: A dictionary containing the echoed prompt string.
    """
    return {"response": prompt.get("prompt", "")}
