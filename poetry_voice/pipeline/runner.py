from __future__ import annotations

import re
from collections.abc import Awaitable, Callable
from pathlib import Path

import structlog

from poetry_voice.audio import post_process_audio
from poetry_voice.config.settings import AppConfig
from poetry_voice.llm.factory import build_llm_provider
from poetry_voice.models import PoemAnnotation, SynthesisResult
from poetry_voice.parser.factory import parse_document
from poetry_voice.pipeline.segmentation import split_into_sentences
from poetry_voice.tts.factory import build_tts_provider

logger = structlog.get_logger(__name__)
ProgressCallback = Callable[[str], Awaitable[None]]


class PoetryVoicePipeline:
    def __init__(self, config: AppConfig) -> None:
        self.config = config
        self.llm = build_llm_provider(config.llm)
        self.tts = build_tts_provider(config.tts)

    async def run(
        self, input_path: Path | str, progress: ProgressCallback | None = None
    ) -> SynthesisResult:
        await _publish(progress, "Lettura del file e riconoscimento formato")
        document = parse_document(input_path)
        logger.info("document_parsed", path=str(document.path), format=document.source_format)
        await _publish(
            progress,
            f"File letto: formato {document.source_format}, {len(document.text)} caratteri",
        )
        text = document.text
        if self.config.pipeline.segmentation == "sentences":
            text = split_into_sentences(text)
            await _publish(progress, "Testo suddiviso in frasi in base alla punteggiatura")
        await _publish(
            progress, f"Analisi LLM con {self.config.llm.provider} / {self.config.llm.model}"
        )
        annotation = await self.llm.analyze(text)
        annotation.language = self.config.llm.language
        annotation.mood = self.config.llm.reading_tone
        annotation.overall_speed = self.config.tts.speed
        annotation.voice_style = _voice_style_for_tone(self.config.llm.reading_tone)
        for line in annotation.lines:
            line.speed = self.config.tts.speed
        logger.info("poem_annotated", title=annotation.title, lines=len(annotation.lines))
        await _publish(
            progress,
            f"Annotazione pronta: {len(annotation.lines)} versi, tono {annotation.mood}, velocita {annotation.overall_speed}",
        )

        output_dir = self.config.pipeline.output_dir
        output_dir.mkdir(parents=True, exist_ok=True)
        stem = _safe_stem(document.path.stem)
        wav_path = output_dir / f"{stem}.raw.wav"
        final_path = output_dir / f"{stem}.{self.config.audio.format}"

        await _publish(
            progress,
            f"Sintesi vocale con {self.config.tts.engine} / {self.config.tts.speaker}",
        )
        await self.tts.synthesize(annotation, wav_path)
        await _publish(
            progress, f"Post-processing audio FFmpeg in formato {self.config.audio.format}"
        )
        await post_process_audio(wav_path, final_path, self.config.audio)
        intermediates = [wav_path] if self.config.pipeline.keep_intermediates else []
        if not self.config.pipeline.keep_intermediates:
            wav_path.unlink(missing_ok=True)
        await _publish(progress, f"Audio generato: {final_path.name}")
        return SynthesisResult(
            audio_path=final_path,
            annotation=annotation,
            source_text=document.text,
            intermediate_files=intermediates,
        )

    async def synthesize_annotation(
        self,
        annotation: PoemAnnotation,
        output_stem: str = "edited-annotation",
        progress: ProgressCallback | None = None,
    ) -> SynthesisResult:
        output_dir = self.config.pipeline.output_dir
        output_dir.mkdir(parents=True, exist_ok=True)
        stem = _safe_stem(output_stem)
        wav_path = output_dir / f"{stem}.raw.wav"
        final_path = output_dir / f"{stem}.{self.config.audio.format}"

        await _publish(
            progress,
            f"Sintesi vocale da anteprima modificata con {self.config.tts.engine} / {self.config.tts.speaker}",
        )
        await self.tts.synthesize(annotation, wav_path)
        await _publish(
            progress, f"Post-processing audio FFmpeg in formato {self.config.audio.format}"
        )
        await post_process_audio(wav_path, final_path, self.config.audio)
        if not self.config.pipeline.keep_intermediates:
            wav_path.unlink(missing_ok=True)
        await _publish(progress, f"Audio generato: {final_path.name}")
        return SynthesisResult(
            audio_path=final_path,
            annotation=annotation,
            source_text="\n".join(line.text for line in annotation.lines),
        )


def _safe_stem(value: str) -> str:
    return re.sub(r"[^a-zA-Z0-9_.-]+", "-", value).strip("-") or "poetry-voice"


def _voice_style_for_tone(tone: str) -> str:
    normalized = tone.lower()
    if normalized in {"neutro", "neutral"}:
        return "neutral"
    if normalized in {"solenne", "profondo", "deep"}:
        return "deep"
    if normalized in {"delicato", "malinconico", "soft"}:
        return "soft"
    if normalized in {"brillante", "bright"}:
        return "bright"
    return "warm"


async def _publish(progress: ProgressCallback | None, message: str) -> None:
    if progress is not None:
        await progress(message)
