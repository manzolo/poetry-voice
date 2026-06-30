from __future__ import annotations

from poetry_voice.config.settings import LLMConfig
from poetry_voice.llm.base import LLMProvider
from poetry_voice.llm.http_json import HttpJsonLLMProvider


def build_llm_provider(config: LLMConfig) -> LLMProvider:
    return HttpJsonLLMProvider(config)
