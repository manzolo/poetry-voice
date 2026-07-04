# Poetry Voice

> 🇮🇹 **[Versione italiana](README.md)**

Poetry Voice is an open source Python application that turns poems into expressive audiobooks.

The goal is not plain text-to-speech. Poetry Voice first analyzes the poem, identifying rhythm, pauses, emotions and emphasis, then sends an annotated reading plan to a configurable TTS engine. The desired result is a warm, elegant, relaxing reading, closer to an attentive human narrator than to a mechanical voice.

The project is designed with special attention to accessibility. A patient, well-modulated voice can become a way to accompany people who cannot see, or see with difficulty, through poems and other texts: the page that cannot be looked at speaks again.

*Inspired by Massimo Bianchini.*

## Accessibility

The attention to accessibility also applies to whoever installs and uses the
program. That is why every operation boils down to **a single command to copy**,
and the web interface is designed for screen readers, high contrast and
keyboard navigation.

## What it does

- Reads poems from TXT, Markdown and PDF files.
- Preserves the original line breaks as much as possible, even from PDFs.
- Uses an LLM to analyze tone, emotion, rhythm, pauses and emphasis.
- Produces an extensible prosodic JSON annotation.
- Sends the annotation to a swappable TTS engine.
- Post-processes the audio with FFmpeg.
- Exports WAV, FLAC, MP3 and optionally OGG.
- Offers both a CLI and an accessible FastAPI web interface.
- Runs locally on CPU or in a Docker container with an NVIDIA GPU and Ollama included.

## How to use it

Pick **one** of the two paths. You do not need both.

### Standalone — no Docker, no GPU (the simplest)

Runs on your computer using the CPU. One command:

```bash
make local
```

Then open `http://127.0.0.1:8000`.

Full guide: **[docs/standalone.md](docs/standalone.md)**.

### Docker with NVIDIA GPU (best quality, Ollama included)

```bash
make setup
make up
```

Then open `http://localhost:8000`.

Full guide: **[docs/docker.md](docs/docker.md)**.

## Architecture

```text
input file
   |
   v
parser
   |
   v
LLM analysis
   |
   v
prosodic JSON annotation
   |
   v
TTS engine
   |
   v
FFmpeg post-processing
   |
   v
final audiobook
```

Main modules:

```text
poetry_voice/
  cli.py             CLI entrypoint
  config/            YAML + Pydantic configuration
  llm/               LLM provider abstraction
  parser/            TXT, Markdown and PDF parsers
  tts/               TTS provider abstraction
  pipeline/          end-to-end orchestration
  ui/                FastAPI web interface
  audio.py           FFmpeg post-processing
  models.py          shared data models
tests/               unit tests
```

## Prosodic annotation

The LLM returns structured JSON like this:

```json
{
  "title": "L'infinito",
  "author": "Giacomo Leopardi",
  "language": "it",
  "mood": "nostalgic",
  "overall_speed": "slow",
  "voice_style": "warm",
  "lines": [
    {
      "text": "Sempre caro mi fu quest'ermo colle,",
      "pause_before": 0.0,
      "pause_after": 0.8,
      "breath_after": false,
      "emphasis": ["Sempre"],
      "emotion": "wonder",
      "volume": 1.0,
      "speed": "slow",
      "pitch": 1.0,
      "metadata": {}
    }
  ],
  "metadata": {}
}
```

The schema is deliberately extensible, so new engines can use richer metadata
without changing the parser or the pipeline.

## Using the web interface

The web UI supports poem upload **or** writing/pasting the text directly
(the "Text source" switch), choice of TTS engine, reading language, tone and
speed, editing of the extracted text, free-form instructions for the LLM,
choice of LLM provider and model (the model field offers a dropdown of models
already downloaded in Ollama, while remaining freely editable), an editable
annotated preview (text, pause and emotion per line, with line reordering),
a progress log with progress bar, audio playback and download.

While processing, the parameters disappear and only the progress remains, with
a **Stop processing** button to cancel the job; the fields come back when the
job finishes, fails or is cancelled.

The text can be split **by line breaks** (default: right for poems) or **by
sentences** based on punctuation (better for prose, where the file's line
breaks carry no rhythmic meaning). Available in the UI, from the CLI
(`--split lines|sentences`) and in `config.yaml` (`pipeline.segmentation`).

The interface is bilingual: Italian and English, with a switcher at the top
right (the choice is remembered). The interface language is independent from
the poem's reading language: the voice list filters automatically to match
the selected engine and reading language.

Suggested flow:

1. Upload a file and generate the first audiobook.
2. The extracted text stays in the form at the top.
3. Edit lines, punctuation, or add instructions.
4. In the annotated preview you can edit each line, its pause and emotion, and reorder lines.
5. `Regenerate from edited preview` synthesizes again without re-running the LLM analysis.
6. `Generate audiobook` re-runs the analysis starting from the edited text.

UI accessibility choices: large text, high contrast, clearly visible keyboard
focus, semantic HTML, explicit labels, screen-reader-friendly structure and
the browser's standard audio controls.

The accessible layout is the default; a **Compact layout** button at the top
switches to a denser rendering (smaller text, two-column fields) for those who
do not need it. The choice is remembered by the browser; contrast and keyboard
focus stay unchanged.

## Configuration

Configuration lives in `config.yaml` (for Docker) or in the defaults (locally).
Example:

```yaml
llm:
  provider: ollama
  model: qwen3:8b
  base_url: http://localhost:11434
  temperature: 0.2
  # Ollama context window: raise it if long texts get truncated.
  num_ctx: 8192
  # Texts beyond this number of lines are analyzed in stanza chunks.
  max_lines_per_chunk: 24
  language: it
  reading_tone: caldo
  reading_speed: slow
  reading_instructions: ""

tts:
  engine: piper
  speaker: it_IT-paola-medium
  language: it
  device: cuda
  model_path: /models/piper/it_IT-paola-medium.onnx
  sample_rate: 24000
  speed: slow
  sentence_silence: 0.8

audio:
  format: mp3
  bitrate: 192k
  lufs: -18
  noise_reduction: false
  fade_ms: 120
  light_compression: true

pipeline:
  output_dir: outputs
  keep_intermediates: false
```

Locally, the `make local-*` targets use `config.local.yaml` and keep data under
`local-data/` (owned by the user, separate from Docker's folders).
`device: cuda` is ignored by Piper anyway, which runs on CPU.

## Supported parsers

| Format | Extension | Implementation |
| --- | --- | --- |
| Plain text | `.txt` | UTF-8 read |
| Markdown | `.md`, `.markdown` | `markdown-it-py` |
| PDF | `.pdf` | layout extraction with `pypdf` |

## LLM providers

The LLM layer is abstract. Current modes are `ollama` (default), `openai` and
`generic`. The provider receives the poem and returns a validated
`PoemAnnotation`. If the LLM call fails, a heuristic fallback generates a basic
annotation to keep the rest of the pipeline usable.

## TTS engines

The TTS layer is abstract. Current adapters are `piper` (default), `kokoro`,
`dia` and `xtts`. The engine is chosen via YAML:

```yaml
tts:
  engine: piper
```

Voices are bound to the engine **and to the language**: the UI only shows the
ones compatible with the selected engine and reading language, and the backend
rejects incompatible combinations instead of silently falling back. From the
CLI, `--language en` without `--speaker` automatically picks a suitable
English voice.

For more natural voices there is the **Kokoro** engine (neural), which
respects per-line pauses. It requires the neural stack: use it via Docker
(recommended) or locally with Python ≤ 3.13 and `espeak-ng` (spacy/kokoro
wheels do not exist for Python 3.14 yet). All per-line pauses are respected
with both Piper and Kokoro.

| Voice | Key | Engine | Language | Notes |
| --- | --- | --- | --- | --- |
| Paola | `it_IT-paola-medium` | piper | it | medium quality, recommended default |
| Riccardo | `it_IT-riccardo-x_low` | piper | it | very light, lower quality |
| Lessac | `en_US-lessac-medium` | piper | en | US English, medium quality |
| Ryan | `en_US-ryan-medium` | piper | en | US English, medium quality |
| Sara | `if_sara` | kokoro | it | neural |
| Nicola | `im_nicola` | kokoro | it | neural |
| Heart | `af_heart` | kokoro | en | US English, neural |
| Michael | `am_michael` | kokoro | en | US English, neural |

If a model is missing, it is downloaded automatically at runtime into
`./models/piper/`. To add more Piper voices, register them in
`poetry_voice/tts/piper_voices.py`.

If an optional neural backend is not available for the current Python/CUDA
environment, Poetry Voice uses `espeak-ng` as an Italian fallback voice, so
the pipeline, UI and post-processing remain usable.

## Audio post-processing

FFmpeg is used for LUFS normalization, light compression, a short fade-in,
MP3/FLAC/WAV/OGG export and configurable bitrate.

## Development

Local setup and quality checks:

```bash
make local-setup
make local-test     # pytest
make local-lint     # ruff + black --check
```

Alternatively, by hand:

```bash
python3.12 -m venv .venv
source .venv/bin/activate
pip install -e ".[dev,tts]"
ruff check . && black --check . && pytest
```

The GitHub Actions CI runs lint, tests and a CPU trial conversion.

### Adding a new LLM provider

1. Create a class implementing `LLMProvider`.
2. Return a validated `PoemAnnotation`.
3. Register the class in `poetry_voice/llm/factory.py`.
4. Add the configuration value to `LLMConfig.provider`.

### Adding a new TTS engine

1. Create an adapter in `poetry_voice/tts/`.
2. Implement `TTSProvider.synthesize(annotation, output_wav)`.
3. Register the adapter in `poetry_voice/tts/factory.py`.
4. Add the configuration value to `TTSConfig.engine`.

## Roadmap

- Better voice presets for Italian.
- Real implementation of the Dia adapter.
- Voice preview before the full render.
- More robust PDF handling.
- Speaker profiles optimized for poetry.
- Optional job queue for long conversions.
- Broader accessibility testing with screen readers.

## License

MIT.
