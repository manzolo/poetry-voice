from __future__ import annotations

from dataclasses import dataclass

from poetry_voice.tts.kokoro_voices import KOKORO_VOICES
from poetry_voice.tts.piper_voices import PIPER_VOICES


@dataclass(frozen=True, slots=True)
class VoiceOption:
    key: str
    label: str
    engine: str
    language: str


def _build_voice_options() -> dict[str, VoiceOption]:
    # Sorgente unica: i cataloghi per motore. Per aggiungere una voce basta
    # registrarla nel file del suo motore (piper_voices.py / kokoro_voices.py);
    # UI e validazione la prendono da qui.
    options: dict[str, VoiceOption] = {}
    for voice in PIPER_VOICES.values():
        options[voice.key] = VoiceOption(
            key=voice.key,
            label=voice.label,
            engine="piper",
            language=voice.language,
        )
    for voice in KOKORO_VOICES.values():
        options[voice.key] = VoiceOption(
            key=voice.key,
            label=voice.label,
            engine="kokoro",
            language=voice.language,
        )
    return options


VOICE_OPTIONS: dict[str, VoiceOption] = _build_voice_options()


def available_voices() -> list[VoiceOption]:
    return list(VOICE_OPTIONS.values())


# Motori che usano una voce dal catalogo. Gli altri (es. xtts, che clona da un
# campione audio) non richiedono una voce registrata.
CATALOG_ENGINES = {"piper", "kokoro"}


def validate_voice_for_engine(engine: str, speaker: str) -> str | None:
    if engine not in CATALOG_ENGINES:
        return None
    option = VOICE_OPTIONS.get(speaker)
    if option is None:
        return f"Voce non registrata: {speaker}"
    if option.engine != engine:
        return f"La voce {option.label} e disponibile solo con il motore {option.engine}."
    return None
