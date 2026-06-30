from __future__ import annotations

import asyncio
import shutil
import tempfile
import urllib.request
import wave
from pathlib import Path

import structlog

from poetry_voice.config.settings import TTSConfig
from poetry_voice.models import LineAnnotation, PoemAnnotation
from poetry_voice.tts.base import TTSProvider
from poetry_voice.tts.fallback import FallbackToneTTSProvider
from poetry_voice.tts.piper_voices import get_piper_voice
from poetry_voice.tts.rendering import ensure_soft_punctuation

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

        lines = [line for line in annotation.lines if line.text.strip()]
        if not lines:
            return await self.fallback.synthesize(annotation, output_wav)

        output_wav.parent.mkdir(parents=True, exist_ok=True)
        # Piper espone solo un silenzio globale (--sentence-silence) e ignora le
        # pause per verso. Per rispettare pause_before/pause_after sintetizziamo
        # ogni verso separatamente e concateniamo inserendo silenzi esatti.
        tmp_dir = Path(tempfile.mkdtemp(prefix="piper-lines-"))
        try:
            rendered: list[tuple[LineAnnotation, Path]] = []
            for index, line in enumerate(lines):
                segment = tmp_dir / f"line_{index:04d}.wav"
                if not await self._render_line(line, model_path, segment):
                    logger.error("piper_failed_using_fallback")
                    return await self.fallback.synthesize(annotation, output_wav)
                rendered.append((line, segment))
            _concatenate_with_pauses(rendered, output_wav)
        finally:
            shutil.rmtree(tmp_dir, ignore_errors=True)
        return output_wav

    async def _render_line(self, line: LineAnnotation, model_path: Path, segment: Path) -> bool:
        process = await asyncio.create_subprocess_exec(
            "piper",
            "--model",
            str(model_path),
            "--length-scale",
            str(_length_scale(self.config.speed)),
            "--sentence-silence",
            "0.0",
            "--output_file",
            str(segment),
            stdin=asyncio.subprocess.PIPE,
        )
        text = ensure_soft_punctuation(line.text.strip())
        await process.communicate(text.encode("utf-8"))
        return process.returncode == 0 and segment.exists()

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


def _concatenate_with_pauses(rendered: list[tuple[LineAnnotation, Path]], output_wav: Path) -> None:
    with wave.open(str(rendered[0][1]), "rb") as first:
        params = first.getparams()
    rate, channels, width = params.framerate, params.nchannels, params.sampwidth

    def silence(seconds: float) -> bytes:
        frames = int(max(0.0, seconds) * rate)
        return b"\x00" * (frames * channels * width)

    with wave.open(str(output_wav), "wb") as out:
        out.setnchannels(channels)
        out.setsampwidth(width)
        out.setframerate(rate)
        for line, segment in rendered:
            if line.pause_before:
                out.writeframes(silence(line.pause_before))
            with wave.open(str(segment), "rb") as seg:
                out.writeframes(seg.readframes(seg.getnframes()))
            out.writeframes(silence(line.pause_after))


def _length_scale(speed: str) -> float:
    return {
        "very_slow": 1.45,
        "slow": 1.22,
        "medium": 1.0,
        "fast": 0.86,
    }[speed]


def _download_file(url: str, path: Path) -> None:
    urllib.request.urlretrieve(url, path)
