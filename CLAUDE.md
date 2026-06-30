# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## What this is

Poetry Voice turns poems (TXT/MD/PDF) into expressive audiobooks. It is **not** plain TTS: an LLM first analyzes the poem to produce a prosodic annotation (pauses, emphasis, emotion, speed per line), and that annotation drives a configurable TTS engine, followed by FFmpeg post-processing. Accessibility (low-vision users) is a primary design goal. Default language is Italian; the README and most user-facing strings are in Italian.

## Project rules

- **Changelog**: every time you commit & push, update `CHANGELOG.md` under the `## [Unreleased]` section, grouping entries into `Aggiunto` / `Modificato` / `Corretto` (Added/Changed/Fixed, in Italian). Keep the changelog entry in the same commit as the change it describes. On a version bump, move `[Unreleased]` under the new version heading with the date (`YYYY-MM-DD`). Format: Keep a Changelog + SemVer.

## Commands

Everything normally runs inside the Docker container (which also runs Ollama and needs an NVIDIA GPU). The `Makefile` is the canonical interface.

```bash
make setup        # config.yaml + dirs + docker build + pull Ollama & Piper models
make up           # start web app (localhost:8000) and Ollama (localhost:11434)
make down
make logs
make shell        # bash inside the container
make gpu-check    # nvidia-smi inside the container

make test         # pytest (runs: docker compose run --rm poetry-voice pytest)
make lint         # ruff check . && black --check .
make convert INPUT=uploads/poem.txt ARGS="--voice piper --format flac"
make cli ARGS="--help"
```

Run a single test (inside container or local venv): `pytest tests/test_pipeline.py::test_name`

Local (no Docker) dev setup:
```bash
python3.12 -m venv .venv && source .venv/bin/activate
pip install -e ".[dev,tts]"
cp config.example.yaml config.yaml
ruff check . && black --check . && pytest
```
Lint config: ruff + black, line length 100, target py312. Ruff enforces type annotations (ANN rules) — annotate new functions. `pytest` uses `asyncio_mode = "auto"`, so `async def test_*` works without decorators.

## Architecture

The pipeline is a linear, layered flow orchestrated by `poetry_voice/pipeline/runner.py` (`PoetryVoicePipeline`):

```
input file → parser → LLM analysis → PoemAnnotation (JSON) → TTS engine → FFmpeg → audiobook
```

`PoemAnnotation` / `LineAnnotation` (`poetry_voice/models.py`) is the central data contract that flows between every layer. It is deliberately extensible (per-line `metadata` dicts) so new engines can carry richer data without changing parser or pipeline.

Each layer is swapped via a factory + config, so adding a backend never touches the rest of the pipeline:

- **Parser** (`parser/factory.py` → `parse_document`): picks TXT/Markdown/PDF by extension. Preserves original line breaks as much as possible.
- **LLM** (`llm/factory.py` → `build_llm_provider`): **always** returns `HttpJsonLLMProvider`. The `provider` config value (`ollama`/`openai`/`generic`) only changes the endpoint and request payload shape inside that one class — there is not a class per provider.
- **TTS** (`tts/factory.py` → `build_tts_provider`): maps the `engine` config string to a provider class (`piper`/`kokoro`/`dia`/`xtts`).

### Graceful degradation is a core pattern, not an edge case

The whole system is built to keep working when heavy/optional dependencies or external services are missing:

- `HttpJsonLLMProvider.analyze` catches **any** exception and falls back to `HeuristicLLMProvider` (a rule-based annotator). A broken/absent LLM still yields a valid `PoemAnnotation`.
- Each neural TTS provider holds a `FallbackToneTTSProvider` and delegates to it when its model is missing or the subprocess fails. The fallback uses `espeak-ng` if present, otherwise synthesizes plain tones. This is why the container starts even when `pip install ".[tts]"` fails.

When debugging "wrong/robotic output", first check the logs (`structlog`) for fallback messages — the real engine may have silently degraded.

### Config drives everything

`config/settings.py` defines the pydantic `AppConfig` (`llm`/`tts`/`audio`/`pipeline`). `load_config` reads `config.yaml` (defaults if absent). Engine/voice/language/format selection happens **only** through config — CLI flags and the web UI mutate this config object before building the pipeline.

Note: after the LLM returns an annotation, `runner.py` **overrides** several annotation fields from config (`language`, `mood` from `reading_tone`, `overall_speed`, per-line `speed`). So config wins over the LLM for those fields.

### Entry points

- CLI (`cli.py`, console script `poetryvoice`): Typer app with `convert` and `web` subcommands. `main()` injects an implicit `convert` when the first arg isn't a known subcommand, so `poetryvoice poem.txt` works.
- Web (`ui/app.py`, started by `poetryvoice web`): FastAPI + Jinja2 accessible UI. `ui/jobs.py` tracks progress for the streaming log shown during analysis/synthesis/post-processing. Supports re-synthesizing from an edited annotation **without** re-running the LLM (`synthesize_annotation`).
- Container: `scripts/start-container.sh` launches `ollama serve`, waits for it, pulls the model (`OLLAMA_MODEL`, gated by `POETRYVOICE_PULL_MODEL`) and the Piper voice, then execs `poetryvoice web`.

## Extending

**New LLM provider mode**: extend `HttpJsonLLMProvider` (endpoint/payload), add the literal to `LLMConfig.provider`. **New TTS engine**: implement `TTSProvider.synthesize(annotation, output_wav)` in a new `tts/` module, register it in `tts/factory.py`, add the literal to `TTSConfig.engine`. **New Piper voice**: register key + language + local path + `.onnx`/`.onnx.json` URLs in `tts/piper_voices.py`; voices are validated against the engine in `tts/voices.py` (`validate_voice_for_engine`) — incompatible engine/voice combos are rejected rather than silently falling back.

## Important constraints

- Requires Python ≥ 3.12.
- Voices are bound to engines: Piper voices (`it_IT-paola-medium`, `it_IT-riccardo-x_low`) only work with `engine: piper`. The UI and CLI reject mismatches via `validate_voice_for_engine`.
- Default TTS voice/model is Italian. Selecting another language without configuring a matching voice will still synthesize with the Italian model.
- Persistent host volumes: `./outputs` (audio), `./uploads` (web uploads), `./models` (Piper/HF/torch caches), `./ollama` (LLM models).
