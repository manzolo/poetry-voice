from __future__ import annotations

import os
from pathlib import Path
from typing import Literal

import yaml
from pydantic import BaseModel, Field


class LLMConfig(BaseModel):
    provider: Literal["ollama", "openai", "generic"] = "ollama"
    model: str = "qwen3:8b"
    base_url: str = "http://localhost:11434"
    api_key: str | None = None
    timeout_seconds: float = 120.0
    temperature: float = Field(default=0.2, ge=0.0, le=2.0)
    # Finestra di contesto per Ollama: i default del server (2048-4096 token)
    # troncano i testi lunghi in silenzio e mandano il modello in loop.
    num_ctx: int = Field(default=8192, ge=1024)
    # Oltre questa soglia l'analisi viene spezzata in blocchi di strofe,
    # annotati separatamente e ricomposti per numero di verso.
    max_lines_per_chunk: int = Field(default=24, ge=4)
    language: str = "it"
    reading_tone: str = "caldo"
    reading_speed: Literal["very_slow", "slow", "medium", "fast"] = "slow"
    reading_instructions: str = ""


class TTSConfig(BaseModel):
    engine: Literal["kokoro", "dia", "xtts", "piper"] = "piper"
    speaker: str = "it_IT-paola-medium"
    # Campione audio di riferimento per la clonazione voce (motore xtts).
    # Se valorizzato e il file esiste, XTTS clona quella voce.
    speaker_wav: str | None = None
    language: str = "it"
    device: Literal["auto", "cuda", "cpu"] = "cuda"
    model_path: str | None = "/models/piper/it_IT-paola-medium.onnx"
    sample_rate: int = 24000
    speed: Literal["very_slow", "slow", "medium", "fast"] = "slow"
    sentence_silence: float = Field(default=0.8, ge=0.0, le=5.0)


class AudioConfig(BaseModel):
    format: Literal["wav", "flac", "mp3", "ogg"] = "mp3"
    bitrate: str = "192k"
    lufs: float = -18.0
    noise_reduction: bool = False
    fade_ms: int = 120
    light_compression: bool = True


class PipelineConfig(BaseModel):
    output_dir: Path = Path("outputs")
    keep_intermediates: bool = False


class AppConfig(BaseModel):
    llm: LLMConfig = Field(default_factory=LLMConfig)
    tts: TTSConfig = Field(default_factory=TTSConfig)
    audio: AudioConfig = Field(default_factory=AudioConfig)
    pipeline: PipelineConfig = Field(default_factory=PipelineConfig)


def load_config(path: Path | str | None = None) -> AppConfig:
    if path is None:
        # POETRYVOICE_CONFIG permette di scegliere un file di config diverso
        # senza passare argomenti (usato dai target "make local-*").
        env_path = os.environ.get("POETRYVOICE_CONFIG")
        default = Path(env_path) if env_path else Path("config.yaml")
        if not default.exists():
            return AppConfig()
        path = default
    config_path = Path(path)
    if not config_path.exists():
        return AppConfig()
    data = yaml.safe_load(config_path.read_text(encoding="utf-8")) or {}
    return AppConfig.model_validate(data)
