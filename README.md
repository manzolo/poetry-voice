# Poetry Voice

Poetry Voice e un'applicazione open source in Python che trasforma poesie in audiolibri espressivi.

L'obiettivo non e fare semplice text-to-speech. Poetry Voice analizza prima la poesia, individua ritmo, pause, emozioni ed enfasi, poi invia un piano di lettura annotato a un motore TTS configurabile. Il risultato desiderato e una lettura calda, elegante e rilassante, piu vicina a un narratore umano attento che a una voce meccanica.

Il progetto e pensato con particolare attenzione all'accessibilita. Una voce paziente e ben modulata puo diventare un modo per accompagnare chi non vede, o vede con difficolta, nell'ascolto di poesie e altri testi: la pagina che non si puo guardare torna comunque a parlare.

*Ispirato da Massimo Bianchini.*

## Accessibilita

L'attenzione all'accessibilita vale anche per chi installa e usa il programma.
Per questo ogni operazione e riducibile a **un solo comando da copiare**, e
l'interfaccia web e progettata per screen reader, alto contrasto e navigazione
da tastiera.

## Cosa fa

- Legge poesie da file TXT, Markdown e PDF.
- Preserva il piu possibile gli a capo originali, anche dai PDF.
- Usa un LLM per analizzare tono, emozione, ritmo, pause ed enfasi.
- Produce un'annotazione prosodica JSON estendibile.
- Invia l'annotazione a un motore TTS sostituibile.
- Esegue post-processing audio con FFmpeg.
- Esporta WAV, FLAC, MP3 e opzionalmente OGG.
- Offre sia una CLI sia una interfaccia web FastAPI accessibile.
- Gira sia in locale su CPU sia in un container Docker con GPU NVIDIA e Ollama incluso.

## Come usarlo

Scegli **una** delle due vie. Non servono entrambe.

### Standalone — senza Docker e senza GPU (la piu semplice)

Gira sul tuo computer usando la CPU. Un comando solo:

```bash
make local
```

Poi apri `http://127.0.0.1:8000`.

Guida completa: **[docs/standalone.md](docs/standalone.md)**.

### Docker con GPU NVIDIA (qualita massima, Ollama incluso)

```bash
make setup
make up
```

Poi apri `http://localhost:8000`.

Guida completa: **[docs/docker.md](docs/docker.md)**.

## Architettura

```text
file input
   |
   v
parser
   |
   v
analisi LLM
   |
   v
annotazione prosodica JSON
   |
   v
motore TTS
   |
   v
post-processing FFmpeg
   |
   v
audiolibro finale
```

Moduli principali:

```text
poetry_voice/
  cli.py             entrypoint CLI
  config/            configurazione YAML + Pydantic
  llm/               astrazione provider LLM
  parser/            parser TXT, Markdown e PDF
  tts/               astrazione provider TTS
  pipeline/          orchestrazione end-to-end
  ui/                interfaccia web FastAPI
  audio.py           post-processing FFmpeg
  models.py          modelli dati condivisi
tests/               test unitari
```

## Annotazione prosodica

Il LLM restituisce JSON strutturato di questo tipo:

```json
{
  "title": "L'infinito",
  "author": "Giacomo Leopardi",
  "language": "it",
  "mood": "nostalgico",
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

Lo schema e volutamente estendibile, cosi nuovi motori possono usare metadati piu ricchi senza modificare parser o pipeline.

## Uso dell'interfaccia web

La UI web supporta upload della poesia, scelta del motore TTS, lingua, tono e
velocita di lettura, modifica del testo estratto, indicazioni libere per il LLM,
scelta di provider e modello LLM, anteprima annotata modificabile (testo, pausa
ed emozione per ogni verso, con riordino dei versi), log di avanzamento con barra
di progresso, ascolto e download dell'audio.

Flusso consigliato:

1. Carica un file e genera il primo audiolibro.
2. Il testo estratto resta nella form in alto.
3. Modifica versi, punteggiatura o aggiungi indicazioni.
4. Nell'anteprima annotata puoi modificare ogni verso, la pausa e l'emozione, e riordinarli.
5. `Rigenera da anteprima modificata` sintetizza di nuovo senza rifare l'analisi LLM.
6. `Genera audiolibro` rifa invece l'analisi partendo dal testo modificato.

Scelte di accessibilita della UI: testo grande, alto contrasto, focus da tastiera
ben visibile, HTML semantico, label esplicite, struttura compatibile con screen
reader e controlli audio standard del browser.

## Configurazione

La configurazione vive in `config.yaml` (per Docker) o nei valori predefiniti
(in locale). Esempio:

```yaml
llm:
  provider: ollama
  model: qwen3:8b
  base_url: http://localhost:11434
  temperature: 0.2
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

In locale i target `make local-*` usano `config.local.yaml` e tengono i dati
sotto `local-data/` (di proprieta dell'utente, separati dalle cartelle di Docker).
`device: cuda` viene comunque ignorato da Piper, che gira su CPU.

## Parser supportati

| Formato | Estensione | Implementazione |
| --- | --- | --- |
| Testo semplice | `.txt` | lettura UTF-8 |
| Markdown | `.md`, `.markdown` | `markdown-it-py` |
| PDF | `.pdf` | estrazione layout con `pypdf` |

## Provider LLM

Il layer LLM e astratto. Le modalita attuali sono `ollama` (predefinito),
`openai` e `generic`. Il provider riceve la poesia e restituisce un
`PoemAnnotation` validato. Se la chiamata al LLM fallisce, un fallback euristico
genera un'annotazione di base per mantenere usabile il resto della pipeline.

## Motori TTS

Il layer TTS e astratto. Gli adapter attuali sono `piper` (predefinito),
`kokoro`, `dia` e `xtts`. Il motore si sceglie via YAML:

```yaml
tts:
  engine: piper
```

Le voci sono legate al motore. `Paola` e `Riccardo` sono voci Piper: la UI le
mostra solo quando il motore selezionato e `Piper`, e il backend rifiuta
combinazioni incompatibili invece di usare silenziosamente il fallback.

| Voce | Chiave | Note |
| --- | --- | --- |
| Paola | `it_IT-paola-medium` | qualita media, default consigliato |
| Riccardo | `it_IT-riccardo-x_low` | molto leggero, qualita inferiore |

Se il modello non e presente, viene scaricato automaticamente a runtime in
`./models/piper/`. Per aggiungere altre voci Piper, registrale in
`poetry_voice/tts/piper_voices.py`.

Se un backend neurale opzionale non e disponibile per l'ambiente Python/CUDA
corrente, Poetry Voice usa `espeak-ng` come voce di ripiego in italiano, cosi
pipeline, UI e post-processing restano utilizzabili.

## Post-processing audio

FFmpeg viene usato per normalizzazione LUFS, compressione leggera, breve
fade-in, esportazione MP3/FLAC/WAV/OGG e bitrate configurabile.

## Sviluppo

Setup locale e controlli qualita:

```bash
make local-setup
make local-test     # pytest
make local-lint     # ruff + black --check
```

In alternativa, a mano:

```bash
python3.12 -m venv .venv
source .venv/bin/activate
pip install -e ".[dev,tts]"
ruff check . && black --check . && pytest
```

La CI su GitHub Actions esegue lint, test e una conversione di prova su CPU.

### Aggiungere un nuovo provider LLM

1. Crea una classe che implementa `LLMProvider`.
2. Restituisci un `PoemAnnotation` validato.
3. Registra la classe in `poetry_voice/llm/factory.py`.
4. Aggiungi il valore di configurazione in `LLMConfig.provider`.

### Aggiungere un nuovo motore TTS

1. Crea un adapter in `poetry_voice/tts/`.
2. Implementa `TTSProvider.synthesize(annotation, output_wav)`.
3. Registra l'adapter in `poetry_voice/tts/factory.py`.
4. Aggiungi il valore di configurazione in `TTSConfig.engine`.

## Roadmap

- Preset vocali migliori per l'italiano.
- Implementazione reale dell'adapter Dia.
- Stitching audio per verso con inserimento di silenzi naturali.
- Anteprima voce prima del rendering completo.
- Gestione PDF piu robusta.
- Profili speaker ottimizzati per poesia.
- Coda job opzionale per conversioni lunghe.
- Test di accessibilita piu estesi con screen reader.

## Licenza

MIT.
