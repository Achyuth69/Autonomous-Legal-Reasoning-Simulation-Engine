"""
Dynamic LLM Router
Supports: Groq, OpenAI, Google Gemini, Anthropic Claude, Mistral, Cohere, Together AI, Ollama
Every session carries its own provider + api_key + model.
"""
from __future__ import annotations
import time
from typing import Dict, Any
from app.core.logging import get_logger

logger = get_logger(__name__)

PROVIDERS: Dict[str, Any] = {
    "groq": {
        "label": "Groq (Free)",
        "url": "https://console.groq.com",
        "free": True,
        "models": [
            "llama-3.3-70b-versatile",
            "llama-3.1-70b-versatile",
            "llama-3.1-8b-instant",
            "llama-3.2-90b-text-preview",
            "gemma2-9b-it",
            "gemma-7b-it",
        ],
        "default_model": "llama-3.1-8b-instant",
    },
    "openai": {
        "label": "OpenAI",
        "url": "https://platform.openai.com/api-keys",
        "free": False,
        "models": [
            "gpt-4o",
            "gpt-4o-mini",
            "gpt-4-turbo",
            "gpt-4",
            "gpt-3.5-turbo",
            "o1-mini",
            "o1-preview",
        ],
        "default_model": "gpt-4o-mini",
    },
    "gemini": {
        "label": "Google Gemini (Free tier)",
        "url": "https://aistudio.google.com/app/apikey",
        "free": True,
        "models": [
            "gemini-2.0-flash",
            "gemini-1.5-flash",
            "gemini-1.5-flash-8b",
            "gemini-1.5-pro",
            "gemini-2.0-flash-thinking-exp",
        ],
        "default_model": "gemini-1.5-flash",
    },
    "anthropic": {
        "label": "Anthropic Claude",
        "url": "https://console.anthropic.com/keys",
        "free": False,
        "models": [
            "claude-3-5-sonnet-20241022",
            "claude-3-5-haiku-20241022",
            "claude-3-opus-20240229",
            "claude-3-sonnet-20240229",
            "claude-3-haiku-20240307",
        ],
        "default_model": "claude-3-5-haiku-20241022",
    },
    "mistral": {
        "label": "Mistral AI",
        "url": "https://console.mistral.ai/api-keys",
        "free": False,
        "models": [
            "mistral-large-latest",
            "mistral-medium-latest",
            "mistral-small-latest",
            "open-mixtral-8x22b",
            "open-mistral-7b",
            "codestral-latest",
        ],
        "default_model": "mistral-small-latest",
    },
    "cohere": {
        "label": "Cohere",
        "url": "https://dashboard.cohere.com/api-keys",
        "free": True,
        "models": [
            "command-r-plus",
            "command-r",
            "command",
            "command-light",
        ],
        "default_model": "command-r",
    },
    "together": {
        "label": "Together AI",
        "url": "https://api.together.xyz/settings/api-keys",
        "free": False,
        "models": [
            "meta-llama/Meta-Llama-3.1-70B-Instruct-Turbo",
            "meta-llama/Meta-Llama-3.1-8B-Instruct-Turbo",
            "mistralai/Mixtral-8x7B-Instruct-v0.1",
            "Qwen/Qwen2.5-72B-Instruct-Turbo",
            "google/gemma-2-27b-it",
        ],
        "default_model": "meta-llama/Meta-Llama-3.1-8B-Instruct-Turbo",
    },
    "ollama": {
        "label": "Ollama (Local)",
        "url": "https://ollama.com",
        "free": True,
        "models": [
            "llama3.2",
            "llama3.1",
            "mistral",
            "gemma2",
            "qwen2.5",
            "phi3.5",
            "deepseek-r1",
        ],
        "default_model": "llama3.2",
    },
}


def get_providers() -> Dict:
    return PROVIDERS


def invoke_llm_sync(
    prompt: str,
    provider: str,
    api_key: str,
    model: str,
    temperature: float = 0.7,
    max_tokens: int = 3000,
    base_url: str = None,
) -> str:
    """Call the LLM synchronously with retry on rate limits."""
    provider = provider.lower().strip()

    for attempt in range(4):
        try:
            if provider == "groq":
                return _groq(prompt, api_key, model, temperature, max_tokens)
            elif provider == "openai":
                return _openai(prompt, api_key, model, temperature, max_tokens)
            elif provider == "gemini":
                return _gemini(prompt, api_key, model, temperature, max_tokens)
            elif provider == "anthropic":
                return _anthropic(prompt, api_key, model, temperature, max_tokens)
            elif provider == "mistral":
                return _mistral(prompt, api_key, model, temperature, max_tokens)
            elif provider == "cohere":
                return _cohere(prompt, api_key, model, temperature, max_tokens)
            elif provider == "together":
                return _together(prompt, api_key, model, temperature, max_tokens)
            elif provider == "ollama":
                return _ollama(prompt, model, temperature, max_tokens, base_url)
            else:
                raise ValueError(f"Unknown provider: {provider}")

        except Exception as e:
            err = str(e)
            is_rate = any(x in err for x in ["429", "rate_limit", "RESOURCE_EXHAUSTED", "too_many_requests", "RateLimitError"])
            if is_rate and attempt < 3:
                wait = 2 ** (attempt + 1)
                logger.warning(f"Rate limit ({provider}), retry in {wait}s [attempt {attempt+1}]")
                time.sleep(wait)
            else:
                raise

    raise RuntimeError(f"Rate limit persisted after retries on {provider}/{model}")


def _groq(prompt, api_key, model, temperature, max_tokens):
    from groq import Groq
    c = Groq(api_key=api_key)
    r = c.chat.completions.create(
        model=model,
        messages=[{"role": "user", "content": prompt}],
        temperature=temperature,
        max_tokens=max_tokens,
    )
    return r.choices[0].message.content.strip()


def _openai(prompt, api_key, model, temperature, max_tokens):
    from openai import OpenAI
    c = OpenAI(api_key=api_key)
    r = c.chat.completions.create(
        model=model,
        messages=[{"role": "user", "content": prompt}],
        temperature=temperature,
        max_tokens=max_tokens,
    )
    return r.choices[0].message.content.strip()


def _gemini(prompt, api_key, model, temperature, max_tokens):
    import google.generativeai as genai
    genai.configure(api_key=api_key)
    m = genai.GenerativeModel(model)
    r = m.generate_content(
        prompt,
        generation_config=genai.types.GenerationConfig(
            temperature=temperature,
            max_output_tokens=max_tokens,
        ),
    )
    return r.text.strip()


def _anthropic(prompt, api_key, model, temperature, max_tokens):
    import anthropic
    c = anthropic.Anthropic(api_key=api_key)
    r = c.messages.create(
        model=model,
        max_tokens=max_tokens,
        messages=[{"role": "user", "content": prompt}],
    )
    return r.content[0].text.strip()


def _mistral(prompt, api_key, model, temperature, max_tokens):
    from mistralai import Mistral
    c = Mistral(api_key=api_key)
    r = c.chat.complete(
        model=model,
        messages=[{"role": "user", "content": prompt}],
        temperature=temperature,
        max_tokens=max_tokens,
    )
    return r.choices[0].message.content.strip()


def _cohere(prompt, api_key, model, temperature, max_tokens):
    import cohere
    c = cohere.ClientV2(api_key=api_key)
    r = c.chat(
        model=model,
        messages=[{"role": "user", "content": prompt}],
        temperature=temperature,
        max_tokens=max_tokens,
    )
    return r.message.content[0].text.strip()


def _together(prompt, api_key, model, temperature, max_tokens):
    from openai import OpenAI
    c = OpenAI(api_key=api_key, base_url="https://api.together.xyz/v1")
    r = c.chat.completions.create(
        model=model,
        messages=[{"role": "user", "content": prompt}],
        temperature=temperature,
        max_tokens=max_tokens,
    )
    return r.choices[0].message.content.strip()


def _ollama(prompt, model, temperature, max_tokens, base_url=None):
    """Local Ollama — no API key needed."""
    import requests, json
    url = (base_url or "http://localhost:11434") + "/api/generate"
    resp = requests.post(url, json={
        "model": model,
        "prompt": prompt,
        "stream": False,
        "options": {"temperature": temperature, "num_predict": max_tokens},
    }, timeout=120)
    resp.raise_for_status()
    return resp.json().get("response", "").strip()
