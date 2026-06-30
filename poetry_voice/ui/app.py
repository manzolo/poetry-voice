from __future__ import annotations

import os
import shutil
from pathlib import Path

from fastapi import FastAPI, File, Form, Request, UploadFile
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from poetry_voice.config import load_config
from poetry_voice.models import PoemAnnotation
from poetry_voice.tts.voices import validate_voice_for_engine
from poetry_voice.ui.jobs import create_annotation_job, create_job, get_job

BASE_DIR = Path(__file__).resolve().parent
# Le cartelle dati sono configurabili: in Docker restano "uploads"/"outputs",
# in locale i target "make local-*" le spostano sotto local-data/ (di proprieta
# dell'utente, cosi non si scontrano con i file root creati dai container).
UPLOAD_DIR = Path(os.environ.get("POETRYVOICE_UPLOAD_DIR", "uploads"))
OUTPUT_DIR = load_config().pipeline.output_dir

app = FastAPI(title="Poetry Voice", description="Lettura espressiva di poesie")
app.mount("/outputs", StaticFiles(directory=str(OUTPUT_DIR), check_dir=False), name="outputs")
templates = Jinja2Templates(directory=str(BASE_DIR / "templates"))


@app.get("/", response_class=HTMLResponse)
async def index(request: Request) -> HTMLResponse:
    return templates.TemplateResponse(request, "index.html")


@app.post("/convert")
async def convert(
    file: UploadFile | None = File(None),
    source_text: str = Form(""),
    reading_instructions: str = Form(""),
    tts_engine: str = Form("piper"),
    tts_speaker: str = Form("it_IT-paola-medium"),
    language: str = Form("it"),
    reading_tone: str = Form("caldo"),
    reading_speed: str = Form("slow"),
    llm_provider: str = Form("ollama"),
    llm_model: str = Form("qwen3:8b"),
) -> JSONResponse:
    validation_error = validate_voice_for_engine(tts_engine, tts_speaker)
    if validation_error:
        return JSONResponse({"error": validation_error}, status_code=400)

    UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
    if source_text.strip():
        destination = UPLOAD_DIR / "edited-poem.txt"
        destination.write_text(source_text, encoding="utf-8")
    elif file is not None and file.filename:
        destination = UPLOAD_DIR / Path(file.filename).name
        with destination.open("wb") as handle:
            shutil.copyfileobj(file.file, handle)
    else:
        return JSONResponse(
            {"error": "Carica un file oppure usa il testo estratto modificabile."},
            status_code=400,
        )

    config = load_config()
    config.tts.engine = tts_engine  # type: ignore[assignment]
    config.tts.speaker = tts_speaker
    config.tts.language = language
    config.tts.speed = reading_speed  # type: ignore[assignment]
    config.llm.language = language
    config.llm.reading_tone = reading_tone
    config.llm.reading_speed = reading_speed  # type: ignore[assignment]
    config.llm.reading_instructions = reading_instructions
    config.llm.provider = llm_provider  # type: ignore[assignment]
    config.llm.model = llm_model
    form_data = {
        "source_text": source_text,
        "reading_instructions": reading_instructions,
        "tts_engine": tts_engine,
        "tts_speaker": tts_speaker,
        "language": language,
        "reading_tone": reading_tone,
        "reading_speed": reading_speed,
        "llm_provider": llm_provider,
        "llm_model": llm_model,
    }
    job = create_job(destination, config, form_data=form_data)
    return JSONResponse({"job_id": job.id})


@app.get("/jobs/{job_id}")
async def job_status(job_id: str) -> JSONResponse:
    job = get_job(job_id)
    if job is None:
        return JSONResponse({"status": "missing", "messages": ["Job non trovato"]}, status_code=404)
    return JSONResponse(
        {
            "status": job.status,
            "messages": job.messages,
            "audio_url": job.audio_url,
            "result_url": f"/result/{job.id}" if job.status == "completed" else None,
            "error": job.error,
        }
    )


@app.post("/synthesize-annotation")
async def synthesize_annotation(payload: dict) -> JSONResponse:
    tts_engine = str(payload.get("tts_engine", "piper"))
    tts_speaker = str(payload.get("tts_speaker", "it_IT-paola-medium"))
    validation_error = validate_voice_for_engine(tts_engine, tts_speaker)
    if validation_error:
        return JSONResponse({"error": validation_error}, status_code=400)

    try:
        annotation = PoemAnnotation.model_validate(payload["annotation"])
    except Exception as exc:
        return JSONResponse({"error": f"Annotazione non valida: {exc}"}, status_code=400)

    config = load_config()
    config.tts.engine = tts_engine  # type: ignore[assignment]
    config.tts.speaker = tts_speaker
    config.tts.language = str(payload.get("language", annotation.language))
    config.tts.speed = str(payload.get("reading_speed", annotation.overall_speed))  # type: ignore[assignment]
    config.llm.language = config.tts.language
    config.llm.reading_tone = str(payload.get("reading_tone", annotation.mood))
    config.llm.reading_speed = config.tts.speed  # type: ignore[assignment]
    form_data = {
        "source_text": "\n".join(line.text for line in annotation.lines),
        "reading_instructions": "",
        "tts_engine": config.tts.engine,
        "tts_speaker": config.tts.speaker,
        "language": config.tts.language,
        "reading_tone": config.llm.reading_tone,
        "reading_speed": config.tts.speed,
        "llm_provider": config.llm.provider,
        "llm_model": config.llm.model,
    }
    job = create_annotation_job(annotation, config, form_data=form_data)
    return JSONResponse({"job_id": job.id})


@app.get("/result/{job_id}", response_class=HTMLResponse)
async def result(request: Request, job_id: str) -> HTMLResponse:
    job = get_job(job_id)
    if job is None or job.status != "completed" or job.annotation is None:
        return templates.TemplateResponse(
            request,
            "index.html",
            {"error": "Risultato non disponibile o job non completato."},
        )
    return templates.TemplateResponse(
        request,
        "index.html",
        {
            "annotation": job.annotation,
            "audio_url": job.audio_url,
            "source_text": job.source_text,
            "form_data": {**job.form_data, "source_text": job.source_text},
        },
    )
