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


def default_voice_for(engine: str, language: str) -> VoiceOption | None:
    """Prima voce a catalogo per motore e lingua (per la scelta automatica)."""
    for option in VOICE_OPTIONS.values():
        if option.engine == engine and option.language == language:
            return option
    return None


# Motori che usano una voce dal catalogo. Gli altri (es. xtts, che clona da un
# campione audio) non richiedono una voce registrata.
CATALOG_ENGINES = {"piper", "kokoro"}

_MESSAGES = {
    "it": {
        "unknown": "Voce non registrata: {speaker}",
        "engine": "La voce {label} e disponibile solo con il motore {engine}.",
        "language": "La voce {label} non e disponibile per la lingua {language}.",
    },
    "en": {
        "unknown": "Voice not registered: {speaker}",
        "engine": "Voice {label} is only available with the {engine} engine.",
        "language": "Voice {label} is not available for language {language}.",
    },
}


def validate_voice_for_engine(
    engine: str, speaker: str, language: str | None = None, ui_lang: str = "it"
) -> str | None:
    """Valida voce/motore e, se indicata, la lingua di lettura.

    Ritorna il messaggio d'errore (nella lingua dell'interfaccia) o None.
    """
    if engine not in CATALOG_ENGINES:
        return None
    messages = _MESSAGES.get(ui_lang, _MESSAGES["it"])
    option = VOICE_OPTIONS.get(speaker)
    if option is None:
        return messages["unknown"].format(speaker=speaker)
    if option.engine != engine:
        return messages["engine"].format(label=option.label, engine=option.engine)
    if language and option.language != language:
        return messages["language"].format(label=option.label, language=language)
    return None
