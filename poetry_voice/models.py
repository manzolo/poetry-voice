from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Literal

from pydantic import BaseModel, Field


Speed = Literal["very_slow", "slow", "medium", "fast"]
VoiceStyle = Literal["warm", "neutral", "bright", "deep", "soft"]


class LineAnnotation(BaseModel):
    text: str
    pause_before: float = Field(default=0.0, ge=0.0, le=5.0)
    pause_after: float = Field(default=0.6, ge=0.0, le=8.0)
    breath_after: bool = False
    emphasis: list[str] = Field(default_factory=list)
    emotion: str = "calm"
    volume: float = Field(default=1.0, ge=0.2, le=2.0)
    speed: Speed | None = None
    pitch: float = Field(default=1.0, ge=0.5, le=1.8)
    metadata: dict[str, Any] = Field(default_factory=dict)


class PoemAnnotation(BaseModel):
    title: str = "Untitled"
    author: str | None = None
    language: str = "it"
    mood: str = "calm"
    overall_speed: Speed = "slow"
    voice_style: VoiceStyle = "warm"
    lines: list[LineAnnotation]
    metadata: dict[str, Any] = Field(default_factory=dict)


@dataclass(slots=True)
class ParsedDocument:
    path: Path
    text: str
    source_format: str
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass(slots=True)
class SynthesisResult:
    audio_path: Path
    annotation: PoemAnnotation
    source_text: str = ""
    intermediate_files: list[Path] = field(default_factory=list)
