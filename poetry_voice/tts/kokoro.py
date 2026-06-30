from __future__ import annotations

from pathlib import Path

import structlog

from poetry_voice.config.settings import TTSConfig
from poetry_voice.models import PoemAnnotation
from poetry_voice.tts.base import TTSProvider
from poetry_voice.tts.fallback import FallbackToneTTSProvider
from poetry_voice.tts.rendering import annotation_to_tts_text

logger = structlog.get_logger(__name__)


class KokoroTTSProvider(TTSProvider):
    def __init__(self, config: TTSConfig) -> None:
        self.config = config
        self.fallback = FallbackToneTTSProvider(config)

    async def synthesize(self, annotation: PoemAnnotation, output_wav: Path) -> Path:
        try:
            from kokoro import KPipeline  # type: ignore[import-not-found]
            import soundfile as sf  # type: ignore[import-not-found]

            pipeline = KPipeline(lang_code=self.config.language[:1])
            script = annotation_to_tts_text(annotation)
            generator = pipeline(script, voice=self.config.speaker)
            audio_segments = [audio for _, _, audio in generator]
            if not audio_segments:
                return await self.fallback.synthesize(annotation, output_wav)
            import numpy as np  # type: ignore[import-not-found]

            audio = np.concatenate(audio_segments)
            output_wav.parent.mkdir(parents=True, exist_ok=True)
            sf.write(output_wav, audio, self.config.sample_rate)
            return output_wav
        except Exception as exc:
            logger.error("kokoro_tts_unavailable_using_fallback", error=str(exc))
            return await self.fallback.synthesize(annotation, output_wav)
