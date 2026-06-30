from __future__ import annotations

from abc import ABC, abstractmethod

from poetry_voice.models import PoemAnnotation


class LLMProvider(ABC):
    @abstractmethod
    async def analyze(self, poem: str) -> PoemAnnotation:
        """Return structured prosodic annotation for a poem."""
