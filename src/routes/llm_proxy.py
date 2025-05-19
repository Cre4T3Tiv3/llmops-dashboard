"""
llm_proxy.py

This module defines FastAPI routes for interacting with a simulated LLM (Large Language Model) endpoint
and retrieving recent LLM usage logs. It supports a mock `/llm` POST endpoint with basic routing logic
between different LLM "models", and logs each request for monitoring. It also provides a `/logs` GET
endpoint for querying recent usage.

Endpoints:
- POST /llm: Simulates an LLM call and logs usage metrics (latency, tokens, user, model).
- GET /logs: Retrieves recent LLM usage logs (limit controlled via query parameter).

Dependencies:
- src.database.log_usage: Persists request metadata.
- src.database.get_recent_logs: Fetches historical usage logs.
"""

from fastapi import APIRouter, Depends, Request, Query
from pydantic import BaseModel
import random
import time
from typing import List
from src.database import log_usage, get_recent_logs
import subprocess

router = APIRouter()

class PromptRequest(BaseModel):
    """
    Schema for incoming LLM prompt request.

    Attributes:
        prompt (str): The user-provided input text to send to the LLM.
    """
    prompt: str

class PromptResponse(BaseModel):
    """
    Schema for LLM response.

    Attributes:
        response (str): The LLM-generated response string.
    """
    response: str

@router.post("/llm", response_model=PromptResponse)
def call_llm(request: Request, body: PromptRequest):
    """
    Handles incoming LLM prompt requests.

    Simulates LLM inference using randomized fallback logic (e.g., 30% chance of switching to a local model).
    Calculates latency and token count, then logs the usage.

    Args:
        request (Request): FastAPI Request object, used to extract user info from headers.
        body (PromptRequest): Pydantic model containing the prompt text.

    Returns:
        PromptResponse: A simulated LLM response with model attribution.
    """
    prompt = body.prompt
    user = request.headers.get("x-user-id", "anonymous")

    start_time = time.time()

    # Simulate fallback model logic
    model_used = "openai-gpt"
    if random.random() < 0.3:
        model_used = "local-ollama"

    latency = time.time() - start_time
    token_count = len(prompt.split())

    log_usage(user=user, prompt=prompt, model=model_used, latency=latency, tokens=token_count)

    return {"response": f"[{model_used.capitalize()}] Answer to: {prompt}"}

@router.get("/logs")
def fetch_logs(limit: int = Query(10, ge=1, le=100)) -> List[dict]:
    """
    Returns a list of the most recent LLM usage logs.

    Args:
        limit (int, optional): Number of log entries to retrieve. Must be between 1 and 100. Default is 10.

    Returns:
        List[dict]: A list of usage logs sorted by most recent first.
    """
    return get_recent_logs(limit=limit)
