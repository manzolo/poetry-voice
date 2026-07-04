from __future__ import annotations

import asyncio
import uuid
from dataclasses import dataclass, field
from pathlib import Path

from poetry_voice.config.settings import AppConfig
from poetry_voice.models import PoemAnnotation
from poetry_voice.pipeline import PoetryVoicePipeline


@dataclass(slots=True)
class ConversionJob:
    id: str
    status: str = "queued"
    messages: list[str] = field(default_factory=list)
    audio_url: str | None = None
    annotation: PoemAnnotation | None = None
    source_text: str = ""
    form_data: dict[str, str] = field(default_factory=dict)
    error: str | None = None
    task: asyncio.Task | None = None


JOBS: dict[str, ConversionJob] = {}


def create_job(
    input_path: Path, config: AppConfig, form_data: dict[str, str] | None = None
) -> ConversionJob:
    job = ConversionJob(id=uuid.uuid4().hex, form_data=form_data or {})
    job.messages.append("Job creato")
    JOBS[job.id] = job
    job.task = asyncio.create_task(_run_job(job, input_path, config))
    return job


def create_annotation_job(
    annotation: PoemAnnotation, config: AppConfig, form_data: dict[str, str] | None = None
) -> ConversionJob:
    job = ConversionJob(id=uuid.uuid4().hex, form_data=form_data or {})
    job.messages.append("Job creato da anteprima modificata")
    JOBS[job.id] = job
    job.task = asyncio.create_task(_run_annotation_job(job, annotation, config))
    return job


def get_job(job_id: str) -> ConversionJob | None:
    return JOBS.get(job_id)


def cancel_job(job_id: str) -> ConversionJob | None:
    """Chiede l'annullamento del job; lo stato passa a "cancelled" appena il
    task viene davvero interrotto (il polling lo vede al giro successivo)."""
    job = JOBS.get(job_id)
    if job is None:
        return None
    if job.status in {"queued", "running"} and job.task is not None:
        job.task.cancel()
    return job


async def _run_job(job: ConversionJob, input_path: Path, config: AppConfig) -> None:
    job.status = "running"

    async def progress(message: str) -> None:
        job.messages.append(message)

    try:
        result = await PoetryVoicePipeline(config).run(input_path, progress=progress)
        job.annotation = result.annotation
        job.audio_url = f"/outputs/{result.audio_path.name}"
        job.source_text = result.source_text
        job.status = "completed"
        job.messages.append("Elaborazione completata")
    except asyncio.CancelledError:
        job.status = "cancelled"
        job.messages.append("Elaborazione annullata")
    except Exception as exc:
        job.status = "failed"
        job.error = str(exc)
        job.messages.append(f"Errore: {exc}")


async def _run_annotation_job(
    job: ConversionJob, annotation: PoemAnnotation, config: AppConfig
) -> None:
    job.status = "running"

    async def progress(message: str) -> None:
        job.messages.append(message)

    try:
        result = await PoetryVoicePipeline(config).synthesize_annotation(
            annotation, progress=progress
        )
        job.annotation = result.annotation
        job.audio_url = f"/outputs/{result.audio_path.name}"
        job.source_text = result.source_text
        job.status = "completed"
        job.messages.append("Elaborazione completata")
    except asyncio.CancelledError:
        job.status = "cancelled"
        job.messages.append("Elaborazione annullata")
    except Exception as exc:
        job.status = "failed"
        job.error = str(exc)
        job.messages.append(f"Errore: {exc}")
