from __future__ import annotations

import json
from typing import Any

import httpx

from poetry_voice.config.settings import LLMConfig
from poetry_voice.llm.base import LLMProvider
from poetry_voice.llm.heuristic import HeuristicLLMProvider
from poetry_voice.llm.prompts import SYSTEM_PROMPT, build_analysis_prompt
from poetry_voice.models import PoemAnnotation


class HttpJsonLLMProvider(LLMProvider):
    def __init__(self, config: LLMConfig) -> None:
        self.config = config
        self.fallback = HeuristicLLMProvider()

    async def analyze(self, poem: str) -> PoemAnnotation:
        try:
            payload = self._payload(poem)
            headers = {"Content-Type": "application/json"}
            if self.config.api_key:
                headers["Authorization"] = f"Bearer {self.config.api_key}"
            async with httpx.AsyncClient(timeout=self.config.timeout_seconds) as client:
                response = await client.post(self._endpoint(), json=payload, headers=headers)
                response.raise_for_status()
            content = self._extract_content(response.json())
            return PoemAnnotation.model_validate_json(content)
        except Exception:
            return await self.fallback.analyze(poem)

    def _endpoint(self) -> str:
        base = self.config.base_url.rstrip("/")
        if self.config.provider == "ollama":
            return f"{base}/api/chat"
        return f"{base}/v1/chat/completions"

    def _payload(self, poem: str) -> dict[str, Any]:
        messages = [
            {"role": "system", "content": SYSTEM_PROMPT},
            {
                "role": "user",
                "content": build_analysis_prompt(
                    poem,
                    language=self.config.language,
                    reading_tone=self.config.reading_tone,
                    speed=self.config.reading_speed,
                    instructions=self.config.reading_instructions,
                ),
            },
        ]
        if self.config.provider == "ollama":
            return {
                "model": self.config.model,
                "messages": messages,
                "stream": False,
                "format": "json",
                "options": {"temperature": self.config.temperature},
            }
        return {
            "model": self.config.model,
            "messages": messages,
            "temperature": self.config.temperature,
            "response_format": {"type": "json_object"},
        }

    def _extract_content(self, data: dict[str, Any]) -> str:
        if self.config.provider == "ollama":
            content = data["message"]["content"]
        else:
            content = data["choices"][0]["message"]["content"]
        json.loads(content)
        return content
