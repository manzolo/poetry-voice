from __future__ import annotations

from pathlib import Path

import structlog

from poetry_voice.config.settings import TTSConfig
from poetry_voice.models import PoemAnnotation
from poetry_voice.tts.base import TTSProvider
from poetry_voice.tts.fallback import FallbackToneTTSProvider
from poetry_voice.tts.rendering import annotation_to_tts_text

logger = structlog.get_logger(__name__)


class XTTSTTSProvider(TTSProvider):
    def __init__(self, config: TTSConfig) -> None:
        self.config = config
        self.fallback = FallbackToneTTSProvider(config)

    async def synthesize(self, annotation: PoemAnnotation, output_wav: Path) -> Path:
        try:
            from TTS.api import TTS  # type: ignore[import-not-found]

            model_name = self.config.model_path or "tts_models/multilingual/multi-dataset/xtts_v2"
            tts = TTS(model_name).to("cuda" if self.config.device == "cuda" else "cpu")
            output_wav.parent.mkdir(parents=True, exist_ok=True)
            tts.tts_to_file(
                text=annotation_to_tts_text(annotation),
                file_path=str(output_wav),
                speaker=self.config.speaker,
                language=self.config.language,
            )
            return output_wav
        except Exception as exc:
            logger.error("xtts_unavailable_using_fallback", error=str(exc))
            return await self.fallback.synthesize(annotation, output_wav)
