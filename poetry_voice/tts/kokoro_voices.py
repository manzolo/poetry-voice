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
    # Il prefisso della voce codifica la lingua Kokoro: i=italiano,
    # a=inglese americano, b=inglese britannico (usato da kokoro.py).
    "af_heart": KokoroVoice(
        key="af_heart", label="Heart - English (US) (Kokoro, neural)", language="en"
    ),
    "am_michael": KokoroVoice(
        key="am_michael", label="Michael - English (US) (Kokoro, neural)", language="en"
    ),
}


def get_kokoro_voice(key: str) -> KokoroVoice | None:
    return KOKORO_VOICES.get(key)
