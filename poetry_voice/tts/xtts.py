from __future__ import annotations

from pathlib import Path

import structlog

from poetry_voice.config.settings import TTSConfig
from poetry_voice.models import PoemAnnotation
from poetry_voice.tts.base import TTSProvider
from poetry_voice.tts.fallback import FallbackToneTTSProvider
from poetry_voice.tts.rendering import ensure_soft_punctuation

logger = structlog.get_logger(__name__)


class XTTSTTSProvider(TTSProvider):
    def __init__(self, config: TTSConfig) -> None:
        self.config = config
        self.fallback = FallbackToneTTSProvider(config)

    async def synthesize(self, annotation: PoemAnnotation, output_wav: Path) -> Path:
        try:
            import numpy as np  # type: ignore[import-not-found]
            import soundfile as sf  # type: ignore[import-not-found]
            from TTS.api import TTS  # type: ignore[import-not-found]

            lines = [line for line in annotation.lines if line.text.strip()]
            if not lines:
                return await self.fallback.synthesize(annotation, output_wav)

            # XTTS v2 clona la voce da un campione di riferimento (speaker_wav).
            speaker_wav = self.config.speaker_wav
            if not speaker_wav or not Path(speaker_wav).exists():
                logger.error("xtts_missing_speaker_wav_using_fallback", speaker_wav=speaker_wav)
                return await self.fallback.synthesize(annotation, output_wav)

            model_name = self.config.model_path or "tts_models/multilingual/multi-dataset/xtts_v2"
            tts = TTS(model_name).to("cuda" if self.config.device == "cuda" else "cpu")
            rate = getattr(getattr(tts, "synthesizer", None), "output_sample_rate", 24000) or 24000

            segments: list = []
            for line in lines:
                if line.pause_before:
                    segments.append(np.zeros(int(line.pause_before * rate), dtype=np.float32))
                text = ensure_soft_punctuation(line.text.strip())
                wav = tts.tts(text=text, speaker_wav=speaker_wav, language=self.config.language)
                segments.append(np.asarray(wav, dtype=np.float32))
                if line.pause_after:
                    segments.append(np.zeros(int(line.pause_after * rate), dtype=np.float32))

            output_wav.parent.mkdir(parents=True, exist_ok=True)
            sf.write(output_wav, np.concatenate(segments), rate)
            return output_wav
        except Exception as exc:
            logger.error("xtts_unavailable_using_fallback", error=str(exc))
            return await self.fallback.synthesize(annotation, output_wav)
