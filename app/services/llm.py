"""
LLM Service — Local inference via SSH Tunnel (Qwen and Gemma).

Uses the OpenAI-compatible chat completions API.
Models are accessed through their respective local endpoints.
"""

from __future__ import annotations

import logging
from enum import Enum
from typing import AsyncGenerator, Optional, List, Dict, Any

from openai import AsyncOpenAI

from app.core.config import settings

logger = logging.getLogger(__name__)


class ModelRole(str, Enum):
    """Which model to use for a given task."""
    # Qwen 27B — strong at structured extraction, risk analysis, complex coding, bilingual
    PRIMARY = "primary"
    # Gemma 4B/9B — strong at synthesis, report writing, creative reasoning, strict logic
    SECONDARY = "secondary"


# ── Local clients (OpenAI-compatible) ────────────────────────

_qwen_client: Optional[AsyncOpenAI] = None
_gemma_client: Optional[AsyncOpenAI] = None


def _get_client(role: ModelRole) -> AsyncOpenAI:
    global _qwen_client, _gemma_client
    if role == ModelRole.PRIMARY:
        if _qwen_client is None:
            _qwen_client = AsyncOpenAI(
                api_key=settings.LOCAL_API_KEY,
                base_url=settings.QWEN_API_BASE,
            )
        return _qwen_client
    else:
        if _gemma_client is None:
            _gemma_client = AsyncOpenAI(
                api_key=settings.LOCAL_API_KEY,
                base_url=settings.GEMMA_API_BASE,
            )
        return _gemma_client


def _get_model_name(role: ModelRole) -> str:
    if role == ModelRole.PRIMARY:
        return settings.QWEN_MODEL
    return settings.GEMMA_MODEL


# ─── Public API ──────────────────────────────────────────────

async def generate(
    prompt: str,
    system_prompt: Optional[str] = None,
    role: ModelRole = ModelRole.SECONDARY,
    temperature: float = 0.7,
    max_tokens: int = 4096,
) -> str:
    """Generate a complete response from the LLM (non-streaming)."""
    client = _get_client(role)
    model = _get_model_name(role)

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
        extra_body={
            "chat_template": "{% for message in messages %}{{'<|im_start|>' + message['role'] + '\\n' + message['content'] + '<|im_end|>\\n'}}{% endfor %}{% if add_generation_prompt %}<|im_start|>assistant\\n{% endif %}"
        }
    )

    content = response.choices[0].message.content or ""
    logger.info(f"LLM response | model={model} | response_len={len(content)}")
    return content


async def stream(
    prompt: str,
    system_prompt: Optional[str] = None,
    role: ModelRole = ModelRole.SECONDARY,
    temperature: float = 0.7,
    max_tokens: int = 4096,
) -> AsyncGenerator[str, None]:
    """Stream response chunks from the LLM."""
    client = _get_client(role)
    model = _get_model_name(role)

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
        extra_body={
            "chat_template": "{% for message in messages %}{{'<|im_start|>' + message['role'] + '\\n' + message['content'] + '<|im_end|>\\n'}}{% endfor %}{% if add_generation_prompt %}<|im_start|>assistant\\n{% endif %}"
        }
    )

    async for chunk in response:
        if chunk.choices and chunk.choices[0].delta.content:
            yield chunk.choices[0].delta.content


async def generate_with_history(
    messages: List[Dict[str, str]],
    system_prompt: Optional[str] = None,
    role: ModelRole = ModelRole.SECONDARY,
    temperature: float = 0.7,
    max_tokens: int = 4096,
) -> str:
    """Generate with full conversation history (for multi-turn chat)."""
    client = _get_client(role)
    model = _get_model_name(role)

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
        extra_body={
            "chat_template": "{% for message in messages %}{{'<|im_start|>' + message['role'] + '\\n' + message['content'] + '<|im_end|>\\n'}}{% endfor %}{% if add_generation_prompt %}<|im_start|>assistant\\n{% endif %}"
        }
    )

    return response.choices[0].message.content or ""


async def stream_with_history(
    messages: List[Dict[str, str]],
    system_prompt: Optional[str] = None,
    role: ModelRole = ModelRole.SECONDARY,
    temperature: float = 0.7,
    max_tokens: int = 4096,
) -> AsyncGenerator[str, None]:
    """Stream with full conversation history."""
    client = _get_client(role)
    model = _get_model_name(role)

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
        extra_body={
            "chat_template": "{% for message in messages %}{{'<|im_start|>' + message['role'] + '\\n' + message['content'] + '<|im_end|>\\n'}}{% endfor %}{% if add_generation_prompt %}<|im_start|>assistant\\n{% endif %}"
        }
    )

    async for chunk in response:
        if chunk.choices and chunk.choices[0].delta.content:
            yield chunk.choices[0].delta.content


async def check_connectivity() -> Dict[str, bool]:
    """Quick check if both models respond."""
    results = {}
    for role_name, role in [("qwen", ModelRole.PRIMARY), ("gemma", ModelRole.SECONDARY)]:
        try:
            resp = await generate("Say OK", role=role, max_tokens=5)
            results[role_name] = len(resp) > 0
        except Exception as e:
            logger.warning(f"LLM connectivity check failed for {role_name}: {e}")
            results[role_name] = False
    return results
