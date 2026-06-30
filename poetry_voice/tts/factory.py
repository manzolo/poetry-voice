from __future__ import annotations

from poetry_voice.config.settings import TTSConfig
from poetry_voice.tts.base import TTSProvider
from poetry_voice.tts.dia import DiaTTSProvider
from poetry_voice.tts.kokoro import KokoroTTSProvider
from poetry_voice.tts.piper import PiperTTSProvider
from poetry_voice.tts.xtts import XTTSTTSProvider


def build_tts_provider(config: TTSConfig) -> TTSProvider:
    providers: dict[str, type[TTSProvider]] = {
        "kokoro": KokoroTTSProvider,
        "dia": DiaTTSProvider,
        "xtts": XTTSTTSProvider,
        "piper": PiperTTSProvider,
    }
    return providers[config.engine](config)
