from __future__ import annotations

from pathlib import Path

import structlog

from poetry_voice.config.settings import TTSConfig
from poetry_voice.models import PoemAnnotation
from poetry_voice.tts.base import TTSProvider
from poetry_voice.tts.fallback import FallbackToneTTSProvider
from poetry_voice.tts.rendering import ensure_soft_punctuation

logger = structlog.get_logger(__name__)


class KokoroTTSProvider(TTSProvider):
    def __init__(self, config: TTSConfig) -> None:
        self.config = config
        self.fallback = FallbackToneTTSProvider(config)

    async def synthesize(self, annotation: PoemAnnotation, output_wav: Path) -> Path:
        try:
            import numpy as np  # type: ignore[import-not-found]
            import soundfile as sf  # type: ignore[import-not-found]
            from kokoro import KPipeline  # type: ignore[import-not-found]

            lines = [line for line in annotation.lines if line.text.strip()]
            if not lines:
                return await self.fallback.synthesize(annotation, output_wav)

            # Il lang_code Kokoro e la prima lettera della voce (if_sara -> "i"
            # italiano, af_heart -> "a" inglese US): derivare da config.language
            # funzionerebbe solo per l'italiano ("en"[:1] non e un codice valido).
            speaker = self.config.speaker or self.config.language
            pipeline = KPipeline(lang_code=speaker[:1])
            rate = self.config.sample_rate
            speed = _speed(self.config.speed)

            # Sintesi verso per verso, con silenzi esatti per rispettare
            # pause_before/pause_after (come per Piper).
            segments: list = []
            for line in lines:
                if line.pause_before:
                    segments.append(np.zeros(int(line.pause_before * rate), dtype=np.float32))
                text = ensure_soft_punctuation(line.text.strip())
                parts = [
                    audio for _, _, audio in pipeline(text, voice=self.config.speaker, speed=speed)
                ]
                if not parts:
                    return await self.fallback.synthesize(annotation, output_wav)
                segments.append(np.concatenate(parts).astype(np.float32))
                if line.pause_after:
                    segments.append(np.zeros(int(line.pause_after * rate), dtype=np.float32))

            output_wav.parent.mkdir(parents=True, exist_ok=True)
            sf.write(output_wav, np.concatenate(segments), rate)
            return output_wav
        except Exception as exc:
            logger.error("kokoro_tts_unavailable_using_fallback", error=str(exc))
            return await self.fallback.synthesize(annotation, output_wav)


def _speed(speed: str) -> float:
    return {
        "very_slow": 0.75,
        "slow": 0.85,
        "medium": 1.0,
        "fast": 1.15,
    }.get(speed, 1.0)
