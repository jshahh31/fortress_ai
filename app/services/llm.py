"""
LLM Service — Local inference via SSH Tunnel (Qwen-2.5-VL).

Uses the OpenAI-compatible chat completions API.
"""

from __future__ import annotations

import logging
from enum import Enum
from typing import AsyncGenerator, Optional, List, Dict, Any

from openai import AsyncOpenAI

from app.core.config import settings

logger = logging.getLogger(__name__)


# ── Local clients (OpenAI-compatible) ────────────────────────

_qwen_client: Optional[AsyncOpenAI] = None

def _get_client() -> AsyncOpenAI:
    global _qwen_client
    if _qwen_client is None:
        _qwen_client = AsyncOpenAI(
            api_key=settings.LOCAL_API_KEY,
            base_url=settings.QWEN_API_BASE,
        )
    return _qwen_client

def _get_model_name() -> str:
    return settings.QWEN_MODEL


# ─── Public API ──────────────────────────────────────────────

async def generate(
    prompt: str,
    system_prompt: Optional[str] = None,
    temperature: float = 0.7,
    max_tokens: int = 4096,
) -> str:
    """Generate a complete response from the LLM (non-streaming)."""
    client = _get_client()
    model = _get_model_name()

    messages: List[Dict[str, Any]] = []
    if system_prompt:
        messages.append({"role": "system", "content": system_prompt})
    messages.append({"role": "user", "content": prompt})

    logger.info(f"LLM generate | model={model} | prompt_len={len(prompt)}")

    response = await client.chat.completions.create(
        model=model,
        messages=messages,
        temperature=temperature,
        max_tokens=max_tokens,
        stream=False,
        presence_penalty=0.6,
        frequency_penalty=0.6,
    )

    content = response.choices[0].message.content or ""
    logger.info(f"LLM response | model={model} | response_len={len(content)}")
    return content


async def stream(
    prompt: str,
    system_prompt: Optional[str] = None,
    temperature: float = 0.7,
    max_tokens: int = 4096,
) -> AsyncGenerator[str, None]:
    """Stream response chunks from the LLM."""
    client = _get_client()
    model = _get_model_name()

    messages: List[Dict[str, Any]] = []
    if system_prompt:
        messages.append({"role": "system", "content": system_prompt})
    messages.append({"role": "user", "content": prompt})

    logger.info(f"LLM stream | model={model} | prompt_len={len(prompt)}")

    response = await client.chat.completions.create(
        model=model,
        messages=messages,
        temperature=temperature,
        max_tokens=max_tokens,
        stream=True,
        presence_penalty=0.6,
        frequency_penalty=0.6,
    )

    async for chunk in response:
        if chunk.choices and chunk.choices[0].delta.content:
            yield chunk.choices[0].delta.content


async def generate_with_history(
    messages: List[Dict[str, str]],
    system_prompt: Optional[str] = None,
    temperature: float = 0.7,
    max_tokens: int = 4096,
) -> str:
    """Generate with full conversation history (for multi-turn chat)."""
    client = _get_client()
    model = _get_model_name()

    api_messages: List[Dict[str, Any]] = []
    if system_prompt:
        api_messages.append({"role": "system", "content": system_prompt})
    api_messages.extend(messages)

    logger.info(f"LLM generate_with_history | model={model} | turns={len(messages)}")

    response = await client.chat.completions.create(
        model=model,
        messages=api_messages,
        temperature=temperature,
        max_tokens=max_tokens,
        stream=False,
        presence_penalty=0.6,
        frequency_penalty=0.6,
    )

    return response.choices[0].message.content or ""


async def stream_with_history(
    messages: List[Dict[str, str]],
    system_prompt: Optional[str] = None,
    temperature: float = 0.7,
    max_tokens: int = 4096,
) -> AsyncGenerator[str, None]:
    """Stream with full conversation history."""
    client = _get_client()
    model = _get_model_name()

    api_messages: List[Dict[str, Any]] = []
    if system_prompt:
        api_messages.append({"role": "system", "content": system_prompt})
    api_messages.extend(messages)

    logger.info(f"LLM stream_with_history | model={model} | turns={len(messages)}")

    response = await client.chat.completions.create(
        model=model,
        messages=api_messages,
        temperature=temperature,
        max_tokens=max_tokens,
        stream=True,
        presence_penalty=0.6,
        frequency_penalty=0.6,
    )

    async for chunk in response:
        if chunk.choices and chunk.choices[0].delta.content:
            yield chunk.choices[0].delta.content


async def check_connectivity() -> Dict[str, bool]:
    """Quick check if the model responds."""
    results = {}
    try:
        resp = await generate("Say OK", max_tokens=5)
        results["qwen"] = len(resp) > 0
    except Exception as e:
        logger.warning(f"LLM connectivity check failed: {e}")
        results["qwen"] = False
    return results
