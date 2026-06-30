from __future__ import annotations

from pathlib import Path

import structlog

from poetry_voice.config.settings import TTSConfig
from poetry_voice.models import PoemAnnotation
from poetry_voice.tts.base import TTSProvider
from poetry_voice.tts.fallback import FallbackToneTTSProvider

logger = structlog.get_logger(__name__)


class DiaTTSProvider(TTSProvider):
    def __init__(self, config: TTSConfig) -> None:
        self.config = config
        self.fallback = FallbackToneTTSProvider(config)

    async def synthesize(self, annotation: PoemAnnotation, output_wav: Path) -> Path:
        # Dia APIs are still moving quickly; keep this adapter isolated for plugin evolution.
        logger.error("dia_adapter_not_configured_using_fallback")
        return await self.fallback.synthesize(annotation, output_wav)
