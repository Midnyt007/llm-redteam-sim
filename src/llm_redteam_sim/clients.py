from __future__ import annotations
import os
import time
from typing import Optional, Dict, Any

import requests

try:
    from openai import OpenAI
except Exception:  # pragma: no cover
    OpenAI = None  # type: ignore


class GenResult:
    def __init__(self, text: str, latency_s: float, provider_meta: dict | None = None):
        self.text = text
        self.latency_s = latency_s
        self.provider_meta = provider_meta or {}


class BaseClient:
    def generate(self, prompt: str, *, system: Optional[str] = None, model: str, temperature: float = 0.2) -> GenResult:
        raise NotImplementedError


class OpenAIClient(BaseClient):
    def __init__(self):
        if OpenAI is None:
            raise RuntimeError("openai package not installed")
        base_url = os.environ.get("OPENAI_BASE_URL")
        api_key = os.environ.get("OPENAI_API_KEY")
        if not api_key:
            raise RuntimeError("OPENAI_API_KEY not set")
        self.client = OpenAI(api_key=api_key, base_url=base_url) if base_url else OpenAI(api_key=api_key)

    def generate(self, prompt: str, *, system: Optional[str] = None, model: str, temperature: float = 0.2) -> GenResult:
        t0 = time.time()
        msgs = []
        if system:
            msgs.append({"role": "system", "content": system})
        msgs.append({"role": "user", "content": prompt})
        resp = self.client.chat.completions.create(model=model, messages=msgs, temperature=temperature)
        txt = (resp.choices[0].message.content or "").strip()
        return GenResult(text=txt, latency_s=time.time() - t0, provider_meta={"model": model})


class OllamaClient(BaseClient):
    def __init__(self):
        self.base = os.environ.get("OLLAMA_BASE_URL", "http://localhost:11434")

    def generate(self, prompt: str, *, system: Optional[str] = None, model: str, temperature: float = 0.2) -> GenResult:
        t0 = time.time()
        payload: Dict[str, Any] = {"model": model, "prompt": prompt, "options": {"temperature": temperature}}
        if system:
            payload["system"] = system
        r = requests.post(f"{self.base}/api/generate", json=payload, timeout=600)
        r.raise_for_status()
        # Streaming responses include multiple lines; join final text if present
        text_parts = []
        for line in r.iter_lines(decode_unicode=True):
            if not line:
                continue
            try:
                obj = requests.utils.json.loads(line)
            except Exception:
                continue
            if "response" in obj:
                text_parts.append(obj["response"])  # incremental
            if obj.get("done"):
                break
        text = "".join(text_parts).strip()
        return GenResult(text=text, latency_s=time.time() - t0, provider_meta={"model": model})


def get_client() -> BaseClient:
    provider = os.environ.get("LLM_PROVIDER", "openai").lower()
    if provider == "openai":
        return OpenAIClient()
    if provider == "ollama":
        return OllamaClient()
    raise RuntimeError(f"Unsupported LLM_PROVIDER: {provider}")
