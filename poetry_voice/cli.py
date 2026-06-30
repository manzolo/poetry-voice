from __future__ import annotations

import asyncio
import sys
from pathlib import Path
from typing import Annotated

import typer
from rich.console import Console

from poetry_voice.config import load_config
from poetry_voice.logging import configure_logging
from poetry_voice.pipeline import PoetryVoicePipeline
from poetry_voice.tts.voices import validate_voice_for_engine

app = typer.Typer(help="Trasforma poesie in audiolibri espressivi.")
console = Console()


def _run_conversion(
    input_file: Path,
    config: Path | None,
    voice: str | None,
    speaker: str | None,
    emotion: str,
    speed: str | None,
    language: str | None,
    tone: str | None,
    output_format: str | None,
    log_level: str,
) -> None:
    configure_logging(log_level)
    app_config = load_config(config)
    if voice:
        app_config.tts.engine = voice  # type: ignore[assignment]
    if speaker:
        app_config.tts.speaker = speaker
    validation_error = validate_voice_for_engine(app_config.tts.engine, app_config.tts.speaker)
    if validation_error:
        raise typer.BadParameter(validation_error)
    if language:
        app_config.llm.language = language
        app_config.tts.language = language
    if tone:
        app_config.llm.reading_tone = tone
    if output_format:
        app_config.audio.format = output_format  # type: ignore[assignment]
    if speed:
        app_config.tts.speed = speed  # type: ignore[assignment]
        app_config.llm.reading_speed = speed  # type: ignore[assignment]
    _ = emotion
    result = asyncio.run(PoetryVoicePipeline(app_config).run(input_file))
    console.print(f"[bold green]Audio generato:[/bold green] {result.audio_path}")
    console.print(f"[bold]Titolo:[/bold] {result.annotation.title}")


@app.command()
def convert(
    input_file: Annotated[Path, typer.Argument(exists=True, readable=True)],
    config: Annotated[Path | None, typer.Option("--config", "-c")] = None,
    voice: Annotated[str | None, typer.Option("--voice")] = None,
    speaker: Annotated[str | None, typer.Option("--speaker")] = None,
    emotion: Annotated[str, typer.Option("--emotion")] = "auto",
    speed: Annotated[str | None, typer.Option("--speed")] = None,
    language: Annotated[str | None, typer.Option("--language")] = None,
    tone: Annotated[str | None, typer.Option("--tone")] = None,
    output_format: Annotated[str | None, typer.Option("--format")] = None,
    log_level: Annotated[str, typer.Option("--log-level")] = "INFO",
) -> None:
    _run_conversion(
        input_file,
        config,
        voice,
        speaker,
        emotion,
        speed,
        language,
        tone,
        output_format,
        log_level,
    )


@app.command()
def web(
    host: Annotated[str, typer.Option("--host")] = "0.0.0.0",
    port: Annotated[int, typer.Option("--port")] = 8000,
) -> None:
    import uvicorn

    uvicorn.run("poetry_voice.ui.app:app", host=host, port=port, reload=False)


def main() -> None:
    args = sys.argv[1:]
    if args and not args[0].startswith("-") and args[0] not in {"convert", "web"}:
        args = ["convert", *args]
    app(args=args)


if __name__ == "__main__":
    main()
