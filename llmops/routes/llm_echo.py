"""
llm_echo.py

This module defines the `/llm/echo` route for sending prompts to a local
Ollama instance via its HTTP API and returning the generated response.

It is intended as a lightweight LLM integration for local inference testing
without requiring OpenAI keys or external network access.

Environment Variables:
    OLLAMA_MODEL (str): Name of the Ollama model to use. Defaults to "llama3".

Dependencies:
    - FastAPI for HTTP routing.
    - Pydantic for request schema validation.
    - HTTPX for async HTTP client support.
"""

import os

import httpx
from fastapi import APIRouter, HTTPException, Request
from pydantic import BaseModel

router = APIRouter()


class PromptRequest(BaseModel):
    """
    Request model for LLM prompt input.

    Attributes:
        prompt (str): The user's input prompt to send to the LLM.
    """

    prompt: str


@router.post("/llm/echo")
async def echo_llm(req: Request, body: PromptRequest):
    """
    POST endpoint to send a prompt to Ollama and return its generated response.

    This route interfaces with Ollama's local HTTP API (`/api/generate`)
    using the configured model, and returns the raw output.

    Args:
        req (Request): FastAPI request object.
        body (PromptRequest): Parsed request body containing the prompt string.

    Returns:
        dict: A dictionary containing:
            - 'prompt': The original input prompt.
            - 'response': The generated response from the LLM.

    Raises:
        HTTPException: If the Ollama call fails or returns an error.
    """
    model = os.getenv("OLLAMA_MODEL", "llama3")

    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            res = await client.post(
                "http://localhost:11434/api/generate",
                json={"model": model, "prompt": body.prompt, "stream": False},
            )
            res.raise_for_status()
            result = res.json()

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Ollama error: {e}")

    return {"prompt": body.prompt, "response": result.get("response", "")}
