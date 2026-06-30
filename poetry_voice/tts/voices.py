from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class VoiceOption:
    key: str
    label: str
    engine: str
    language: str


VOICE_OPTIONS: dict[str, VoiceOption] = {
    "it_IT-paola-medium": VoiceOption(
        key="it_IT-paola-medium",
        label="Paola - italiano, qualita media",
        engine="piper",
        language="it",
    ),
    "it_IT-riccardo-x_low": VoiceOption(
        key="it_IT-riccardo-x_low",
        label="Riccardo - italiano, molto leggero",
        engine="piper",
        language="it",
    ),
}


def validate_voice_for_engine(engine: str, speaker: str) -> str | None:
    option = VOICE_OPTIONS.get(speaker)
    if option is None:
        return f"Voce non registrata: {speaker}"
    if option.engine != engine:
        return f"La voce {option.label} e disponibile solo con il motore {option.engine}."
    return None
