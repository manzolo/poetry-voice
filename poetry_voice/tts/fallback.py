from __future__ import annotations

import asyncio
import math
import re
import shutil
import wave
from pathlib import Path

from poetry_voice.config.settings import TTSConfig
from poetry_voice.models import PoemAnnotation
from poetry_voice.tts.base import TTSProvider
from poetry_voice.tts.rendering import annotation_to_tts_text


class FallbackToneTTSProvider(TTSProvider):
    """Fallback TTS used when the selected neural engine is not installed."""

    def __init__(self, config: TTSConfig) -> None:
        self.config = config

    async def synthesize(self, annotation: PoemAnnotation, output_wav: Path) -> Path:
        if shutil.which("espeak-ng"):
            return await self._synthesize_with_espeak(annotation, output_wav)
        return self._synthesize_tone(annotation, output_wav)

    async def _synthesize_with_espeak(self, annotation: PoemAnnotation, output_wav: Path) -> Path:
        output_wav.parent.mkdir(parents=True, exist_ok=True)
        text_path = output_wav.with_suffix(".fallback.txt")
        script = annotation_to_tts_text(annotation)
        clean_script = re.sub(r"\n{2,}", ".\n", script)
        text_path.write_text(clean_script, encoding="utf-8")
        process = await asyncio.create_subprocess_exec(
            "espeak-ng",
            "-v",
            "it",
            "-s",
            str(_espeak_speed(self.config.speed)),
            "-p",
            "35",
            "-w",
            str(output_wav),
            "-f",
            str(text_path),
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
        )
        _, stderr = await process.communicate()
        text_path.unlink(missing_ok=True)
        if process.returncode != 0:
            raise RuntimeError(
                f"Fallback espeak-ng non riuscito: {stderr.decode('utf-8', errors='ignore')}"
            )
        return output_wav

    def _synthesize_tone(self, annotation: PoemAnnotation, output_wav: Path) -> Path:
        output_wav.parent.mkdir(parents=True, exist_ok=True)
        duration = max(2.0, sum(0.25 + line.pause_after for line in annotation.lines))
        sample_rate = self.config.sample_rate
        amplitude = 1200
        with wave.open(str(output_wav), "w") as wav:
            wav.setnchannels(1)
            wav.setsampwidth(2)
            wav.setframerate(sample_rate)
            for index in range(int(duration * sample_rate)):
                sample = int(amplitude * math.sin(2 * math.pi * 220 * index / sample_rate))
                wav.writeframesraw(sample.to_bytes(2, byteorder="little", signed=True))
        return output_wav


def _espeak_speed(speed: str) -> int:
    return {
        "very_slow": 105,
        "slow": 125,
        "medium": 145,
        "fast": 170,
    }[speed]
