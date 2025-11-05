"""
GPT API Client with caching, retry logic, and schema validation
"""

import os
import json
import hashlib
from pathlib import Path
from typing import Dict, Any, Optional
from functools import wraps
import time

import openai
from dotenv import load_dotenv
from tenacity import retry, stop_after_attempt, wait_exponential
from loguru import logger

# Load environment variables
load_dotenv()

# OpenAI Configuration
openai.api_key = os.getenv("OPENAI_API_KEY")
DEFAULT_MODEL = os.getenv("OPENAI_MODEL", "gpt-4o")
DEFAULT_TEMPERATURE = float(os.getenv("OPENAI_TEMPERATURE", "0.0"))
DEFAULT_MAX_TOKENS = int(os.getenv("OPENAI_MAX_TOKENS", "4096"))
MAX_RETRIES = int(os.getenv("MAX_RETRIES", "3"))

# Cache Configuration
CACHE_ENABLED = os.getenv("CACHE_ENABLED", "true").lower() == "true"
CACHE_DIR = Path(os.getenv("CACHE_DIR", "cache/gpt_responses"))
CACHE_DIR.mkdir(parents=True, exist_ok=True)


def _generate_cache_key(prompt: str, model: str, temperature: float) -> str:
    """Generate cache key from prompt and parameters"""
    key_string = f"{prompt}|{model}|{temperature}"
    return hashlib.sha256(key_string.encode()).hexdigest()


def _get_from_cache(cache_key: str) -> Optional[Dict[str, Any]]:
    """Retrieve cached response if exists"""
    if not CACHE_ENABLED:
        return None

    cache_file = CACHE_DIR / f"{cache_key}.json"
    if cache_file.exists():
        logger.info(f"[CACHE HIT] {cache_key[:8]}...")
        return json.loads(cache_file.read_text(encoding='utf-8'))

    logger.info(f"[CACHE MISS] {cache_key[:8]}...")
    return None


def _save_to_cache(cache_key: str, response: Dict[str, Any]) -> None:
    """Save response to cache"""
    if not CACHE_ENABLED:
        return

    cache_file = CACHE_DIR / f"{cache_key}.json"
    cache_file.write_text(json.dumps(response, indent=2, ensure_ascii=False), encoding='utf-8')
    logger.info(f"[CACHE SAVE] {cache_key[:8]}...")


def call_gpt(
    prompt: str,
    model: str = DEFAULT_MODEL,
    temperature: float = DEFAULT_TEMPERATURE,
    max_tokens: int = DEFAULT_MAX_TOKENS,
    response_format: Optional[Dict[str, str]] = None,
    system_prompt: Optional[str] = None,
) -> Dict[str, Any]:
    """
    Call GPT API without caching

    Args:
        prompt: User prompt
        model: GPT model name
        temperature: Sampling temperature (0.0 for deterministic)
        max_tokens: Maximum tokens to generate
        response_format: Force response format (e.g., {"type": "json_object"})
        system_prompt: Optional system prompt

    Returns:
        Parsed JSON response from GPT
    """
    messages = []

    if system_prompt:
        messages.append({"role": "system", "content": system_prompt})

    messages.append({"role": "user", "content": prompt})

    logger.info(f"[GPT CALL] Model={model}, Temp={temperature}, Tokens<={max_tokens}")

    try:
        start_time = time.time()

        kwargs = {
            "model": model,
            "messages": messages,
            "temperature": temperature,
            "max_tokens": max_tokens,
        }

        if response_format:
            kwargs["response_format"] = response_format

        response = openai.chat.completions.create(**kwargs)

        elapsed = time.time() - start_time
        content = response.choices[0].message.content

        logger.info(f"[GPT SUCCESS] Elapsed={elapsed:.2f}s, Response length={len(content)} chars")

        # Try to parse as JSON
        try:
            parsed = json.loads(content)
            return parsed
        except json.JSONDecodeError:
            logger.warning("[GPT WARNING] Response is not valid JSON, returning raw text")
            return {"raw_text": content}

    except Exception as e:
        logger.error(f"[GPT ERROR] {type(e).__name__}: {e}")
        raise


def cached_gpt_call(
    prompt: str,
    model: str = DEFAULT_MODEL,
    temperature: float = DEFAULT_TEMPERATURE,
    max_tokens: int = DEFAULT_MAX_TOKENS,
    response_format: Optional[Dict[str, str]] = None,
    system_prompt: Optional[str] = None,
) -> Dict[str, Any]:
    """
    Call GPT API with caching

    Same parameters as call_gpt(), but checks cache first.
    """
    cache_key = _generate_cache_key(prompt, model, temperature)

    # Check cache
    cached_response = _get_from_cache(cache_key)
    if cached_response is not None:
        return cached_response

    # Call GPT
    response = call_gpt(
        prompt=prompt,
        model=model,
        temperature=temperature,
        max_tokens=max_tokens,
        response_format=response_format,
        system_prompt=system_prompt,
    )

    # Save to cache
    _save_to_cache(cache_key, response)

    return response


@retry(
    stop=stop_after_attempt(MAX_RETRIES),
    wait=wait_exponential(multiplier=1, min=1, max=10),
    reraise=True
)
def robust_gpt_call(
    prompt: str,
    model: str = DEFAULT_MODEL,
    temperature: float = DEFAULT_TEMPERATURE,
    max_tokens: int = DEFAULT_MAX_TOKENS,
    response_format: Optional[Dict[str, str]] = None,
    system_prompt: Optional[str] = None,
    schema_path: Optional[str] = None,
) -> Dict[str, Any]:
    """
    Call GPT API with retry logic and optional schema validation

    Automatically retries on:
    - Rate limit errors
    - Network errors
    - Invalid JSON (if response_format is json_object)

    Args:
        Same as call_gpt(), plus:
        schema_path: Optional path to JSON schema for validation

    Returns:
        Parsed and validated JSON response
    """
    try:
        response = cached_gpt_call(
            prompt=prompt,
            model=model,
            temperature=temperature,
            max_tokens=max_tokens,
            response_format=response_format,
            system_prompt=system_prompt,
        )

        # Validate against schema if provided
        if schema_path:
            from .schema_validator import validate_schema

            if not validate_schema(response, schema_path):
                raise ValueError(f"Response does not match schema: {schema_path}")

        return response

    except openai.RateLimitError as e:
        logger.warning(f"[RETRY] Rate limit hit: {e}")
        raise

    except json.JSONDecodeError as e:
        logger.warning(f"[RETRY] Invalid JSON: {e}")
        raise

    except Exception as e:
        logger.error(f"[ERROR] {type(e).__name__}: {e}")
        raise


# ===== Token Counting =====

def count_tokens(text: str, model: str = DEFAULT_MODEL) -> int:
    """
    Count tokens in text using tiktoken
    """
    import tiktoken

    try:
        encoding = tiktoken.encoding_for_model(model)
    except KeyError:
        encoding = tiktoken.get_encoding("cl100k_base")  # Default for GPT-4

    return len(encoding.encode(text))


def estimate_cost(
    input_tokens: int,
    output_tokens: int,
    model: str = DEFAULT_MODEL
) -> float:
    """
    Estimate API cost based on token counts

    Pricing (as of 2024):
    - gpt-4o: $5/1M input tokens, $15/1M output tokens
    """
    if "gpt-4o" in model:
        input_cost = input_tokens * 5 / 1_000_000
        output_cost = output_tokens * 15 / 1_000_000
    elif "gpt-4" in model:
        input_cost = input_tokens * 30 / 1_000_000
        output_cost = output_tokens * 60 / 1_000_000
    else:
        # Default to gpt-4o pricing
        input_cost = input_tokens * 5 / 1_000_000
        output_cost = output_tokens * 15 / 1_000_000

    return input_cost + output_cost
