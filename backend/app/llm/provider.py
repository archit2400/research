"""Provider-agnostic LLM client supporting Groq, Ollama, and OpenAI."""
from __future__ import annotations

import json
import re
import time
from typing import Any, Dict, List, Optional
import requests

from backend.app.config import settings

FALLBACK_GROQ_MODELS = [
    "openai/gpt-oss-20b",
    "qwen/qwen3.8-27b",
    "openai/gpt-oss-120b",
]

class LLMProvider:
    """Unified LLM client with automatic JSON repair and provider fallbacks."""

    def __init__(self):
        self.provider = settings.LLM_PROVIDER
        self.groq_api_key = settings.GROQ_API_KEY
        self.groq_model = settings.GROQ_MODEL
        self.groq_base_url = settings.GROQ_BASE_URL.rstrip("/")
        
        self.ollama_base_url = settings.OLLAMA_BASE_URL.rstrip("/")
        self.ollama_model = settings.OLLAMA_MODEL
        
        self.openai_api_key = settings.OPENAI_API_KEY
        self.openai_model = settings.OPENAI_MODEL
        self.openai_base_url = settings.OPENAI_BASE_URL.rstrip("/")

    def complete(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        json_mode: bool = False,
        temperature: float = 0.1,
        max_tokens: int = 3500,
    ) -> str:
        """Execute chat completion across configured provider."""
        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": prompt})

        if self.provider == "groq" and self.groq_api_key:
            return self._call_groq(messages, json_mode, temperature, max_tokens)
        elif self.provider == "ollama":
            return self._call_ollama(messages, json_mode, temperature, max_tokens)
        elif self.provider == "openai" and self.openai_api_key:
            return self._call_openai(messages, json_mode, temperature, max_tokens)
        else:
            # Fallback to Groq if key exists, else Ollama, else Mock
            if self.groq_api_key:
                return self._call_groq(messages, json_mode, temperature, max_tokens)
            try:
                return self._call_ollama(messages, json_mode, temperature, max_tokens)
            except Exception:
                raise RuntimeError("No LLM provider available. Please set GROQ_API_KEY or start Ollama.")

    def _call_groq(
        self,
        messages: List[Dict[str, str]],
        json_mode: bool,
        temperature: float,
        max_tokens: int,
    ) -> str:
        url = f"{self.groq_base_url}/chat/completions"
        headers = {
            "Authorization": f"Bearer {self.groq_api_key}",
            "Content-Type": "application/json",
            "User-Agent": "ResearchPilot/1.0",
        }

        # Try active model then fallback models
        models_to_try = [self.groq_model] + [m for m in FALLBACK_GROQ_MODELS if m != self.groq_model]
        last_error = None

        for model_name in models_to_try:
            payload: Dict[str, Any] = {
                "model": model_name,
                "messages": messages,
                "temperature": temperature,
                "max_tokens": max_tokens,
            }
            if json_mode:
                payload["response_format"] = {"type": "json_object"}

            try:
                resp = requests.post(url, headers=headers, json=payload, timeout=90)
                if resp.status_code == 200:
                    data = resp.json()
                    return data["choices"][0]["message"]["content"]
                
                # Check for rate limit or model not found
                if resp.status_code in (404, 429, 400):
                    last_error = f"Groq error ({resp.status_code}) on {model_name}: {resp.text}"
                    time.sleep(1.0)
                    continue
                resp.raise_for_status()
            except Exception as e:
                last_error = str(e)
                time.sleep(0.5)
                continue

        raise RuntimeError(f"All Groq model attempts failed. Last error: {last_error}")

    def _call_ollama(
        self,
        messages: List[Dict[str, str]],
        json_mode: bool,
        temperature: float,
        max_tokens: int,
    ) -> str:
        url = f"{self.ollama_base_url}/chat/completions"
        payload: Dict[str, Any] = {
            "model": self.ollama_model,
            "messages": messages,
            "temperature": temperature,
            "options": {"num_predict": max_tokens},
        }
        if json_mode:
            payload["format"] = "json"

        resp = requests.post(url, json=payload, timeout=120)
        resp.raise_for_status()
        data = resp.json()
        return data["choices"][0]["message"]["content"]

    def _call_openai(
        self,
        messages: List[Dict[str, str]],
        json_mode: bool,
        temperature: float,
        max_tokens: int,
    ) -> str:
        url = f"{self.openai_base_url}/chat/completions"
        headers = {
            "Authorization": f"Bearer {self.openai_api_key}",
            "Content-Type": "application/json",
        }
        payload: Dict[str, Any] = {
            "model": self.openai_model,
            "messages": messages,
            "temperature": temperature,
            "max_tokens": max_tokens,
        }
        if json_mode:
            payload["response_format"] = {"type": "json_object"}

        resp = requests.post(url, headers=headers, json=payload, timeout=90)
        resp.raise_for_status()
        data = resp.json()
        return data["choices"][0]["message"]["content"]

    def complete_json(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        retries: int = 2,
    ) -> Any:
        """Call LLM and reliably parse output as JSON."""
        full_system = (system_prompt or "") + "\nCRITICAL: Respond ONLY with a valid JSON object. Do not wrap in conversational markdown."
        raw_text = ""
        for attempt in range(retries + 1):
            try:
                raw_text = self.complete(prompt, system_prompt=full_system, json_mode=True)
                return self.parse_json_safely(raw_text)
            except Exception as e:
                if attempt == retries:
                    # Last attempt: try manual extraction
                    return self.parse_json_safely(raw_text)
                time.sleep(1.0)
        raise ValueError(f"Failed to parse JSON response: {raw_text[:200]}")

    @staticmethod
    def parse_json_safely(text: str) -> Any:
        """Extract and parse JSON object or array from LLM response."""
        text = text.strip()
        # Remove markdown code fences if present
        if text.startswith("```json"):
            text = text[7:]
        elif text.startswith("```"):
            text = text[3:]
        if text.endswith("```"):
            text = text[:-3]
        text = text.strip()

        try:
            return json.loads(text)
        except json.JSONDecodeError:
            # Match outermost curly braces or brackets
            brace_match = re.search(r"(\{[\s\S]*\}|\[[\s\S]*\])", text)
            if brace_match:
                return json.loads(brace_match.group(1))
            raise


# Global singleton instance
llm = LLMProvider()
