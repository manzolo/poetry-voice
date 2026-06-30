from __future__ import annotations

import asyncio
import urllib.request
from pathlib import Path

import structlog

from poetry_voice.config.settings import TTSConfig
from poetry_voice.models import PoemAnnotation
from poetry_voice.tts.base import TTSProvider
from poetry_voice.tts.fallback import FallbackToneTTSProvider
from poetry_voice.tts.piper_voices import get_piper_voice
from poetry_voice.tts.rendering import annotation_to_tts_text

logger = structlog.get_logger(__name__)


class PiperTTSProvider(TTSProvider):
    def __init__(self, config: TTSConfig) -> None:
        self.config = config
        self.fallback = FallbackToneTTSProvider(config)

    async def synthesize(self, annotation: PoemAnnotation, output_wav: Path) -> Path:
        model_path = await self._ensure_model()
        if model_path is None:
            logger.error("piper_model_path_missing_using_fallback")
            return await self.fallback.synthesize(annotation, output_wav)
        output_wav.parent.mkdir(parents=True, exist_ok=True)
        process = await asyncio.create_subprocess_exec(
            "piper",
            "--model",
            str(model_path),
            "--length-scale",
            str(_length_scale(self.config.speed)),
            "--sentence-silence",
            str(self.config.sentence_silence),
            "--output_file",
            str(output_wav),
            stdin=asyncio.subprocess.PIPE,
        )
        await process.communicate(annotation_to_tts_text(annotation).encode("utf-8"))
        if process.returncode != 0:
            logger.error("piper_failed_using_fallback", returncode=process.returncode)
            return await self.fallback.synthesize(annotation, output_wav)
        return output_wav

    async def _ensure_model(self) -> Path | None:
        voice = get_piper_voice(self.config.speaker)
        if voice is None:
            return Path(self.config.model_path) if self.config.model_path else None

        model_path = voice.model_path
        config_path = Path(f"{model_path}.json")
        if model_path.exists() and config_path.exists():
            return model_path

        logger.info("piper_voice_download_started", voice=voice.key, path=str(model_path))
        model_path.parent.mkdir(parents=True, exist_ok=True)
        try:
            await asyncio.to_thread(_download_file, voice.model_url, model_path)
            await asyncio.to_thread(_download_file, voice.config_url, config_path)
        except Exception as exc:
            logger.error("piper_voice_download_failed", voice=voice.key, error=str(exc))
            fallback_path = Path(self.config.model_path) if self.config.model_path else None
            return fallback_path if fallback_path and fallback_path.exists() else None

        logger.info("piper_voice_download_completed", voice=voice.key, path=str(model_path))
        return model_path


def _length_scale(speed: str) -> float:
    return {
        "very_slow": 1.45,
        "slow": 1.22,
        "medium": 1.0,
        "fast": 0.86,
    }[speed]


def _download_file(url: str, path: Path) -> None:
    urllib.request.urlretrieve(url, path)
