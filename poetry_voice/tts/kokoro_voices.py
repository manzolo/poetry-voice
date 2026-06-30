from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class KokoroVoice:
    key: str
    label: str
    language: str


# Voci Kokoro (neurali). Kokoro scarica da solo i pesi della voce al primo uso.
# Per aggiungere una voce basta registrarla qui: la UI e la validazione la
# prendono dal catalogo unico in voices.py.
KOKORO_VOICES: dict[str, KokoroVoice] = {
    "if_sara": KokoroVoice(key="if_sara", label="Sara - italiano (Kokoro, neurale)", language="it"),
    "im_nicola": KokoroVoice(
        key="im_nicola", label="Nicola - italiano (Kokoro, neurale)", language="it"
    ),
}


def get_kokoro_voice(key: str) -> KokoroVoice | None:
    return KOKORO_VOICES.get(key)
