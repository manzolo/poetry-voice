from __future__ import annotations

from abc import ABC, abstractmethod
from pathlib import Path

from poetry_voice.models import PoemAnnotation


class TTSProvider(ABC):
    @abstractmethod
    async def synthesize(self, annotation: PoemAnnotation, output_wav: Path) -> Path:
        """Generate a WAV file from an annotated poem."""
