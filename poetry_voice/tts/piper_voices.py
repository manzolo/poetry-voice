from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True, slots=True)
class PiperVoice:
    key: str
    label: str
    language: str
    model_path: Path
    model_url: str
    config_url: str


PIPER_VOICES: dict[str, PiperVoice] = {
    "it_IT-paola-medium": PiperVoice(
        key="it_IT-paola-medium",
        label="Paola - italiano, qualita media",
        language="it",
        model_path=Path("/models/piper/it_IT-paola-medium.onnx"),
        model_url=(
            "https://huggingface.co/rhasspy/piper-voices/resolve/main/"
            "it/it_IT/paola/medium/it_IT-paola-medium.onnx"
        ),
        config_url=(
            "https://huggingface.co/rhasspy/piper-voices/resolve/main/"
            "it/it_IT/paola/medium/it_IT-paola-medium.onnx.json"
        ),
    ),
    "it_IT-riccardo-x_low": PiperVoice(
        key="it_IT-riccardo-x_low",
        label="Riccardo - italiano, molto leggero",
        language="it",
        model_path=Path("/models/piper/it_IT-riccardo-x_low.onnx"),
        model_url=(
            "https://huggingface.co/rhasspy/piper-voices/resolve/main/"
            "it/it_IT/riccardo/x_low/it_IT-riccardo-x_low.onnx"
        ),
        config_url=(
            "https://huggingface.co/rhasspy/piper-voices/resolve/main/"
            "it/it_IT/riccardo/x_low/it_IT-riccardo-x_low.onnx.json"
        ),
    ),
}


def get_piper_voice(key: str) -> PiperVoice | None:
    return PIPER_VOICES.get(key)
