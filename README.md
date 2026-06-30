# Poetry Voice

Poetry Voice e un'applicazione open source in Python che trasforma poesie in audiolibri espressivi.

L'obiettivo non e fare semplice text-to-speech. Poetry Voice analizza prima la poesia, individua ritmo, pause, emozioni ed enfasi, poi invia un piano di lettura annotato a un motore TTS configurabile. Il risultato desiderato e una lettura calda, elegante e rilassante, piu vicina a un narratore umano attento che a una voce meccanica.

Il progetto e pensato con particolare attenzione all'accessibilita. Una voce paziente e ben modulata puo diventare un modo per accompagnare chi non vede, o vede con difficolta, nell'ascolto di poesie e altri testi: la pagina che non si puo guardare torna comunque a parlare.

*Ispirato da Massimo Bianchini.*

## Cosa Fa

- Legge poesie da file TXT, Markdown e PDF.
- Preserva il piu possibile gli a capo originali, anche dai PDF.
- Usa un LLM per analizzare tono, emozione, ritmo, pause ed enfasi.
- Produce un'annotazione prosodica JSON estendibile.
- Invia l'annotazione a un motore TTS sostituibile.
- Esegue post-processing audio con FFmpeg.
- Esporta WAV, FLAC, MP3 e opzionalmente OGG.
- Offre sia una CLI sia una interfaccia web FastAPI accessibile.
- Gira in un container Docker con GPU NVIDIA e Ollama incluso.

## Stato Del Progetto

Questo repository fornisce una base modulare funzionante:

- pipeline principale implementata;
- runtime Docker GPU implementato;
- Ollama eseguito dentro lo stesso container;
- livelli parser, LLM, TTS, audio e UI separati;
- motori TTS implementati come adapter sostituibili;
- fallback vocale `espeak-ng` disponibile quando un backend TTS opzionale non e installato.

Alcuni backend TTS, specialmente quelli neurali piu grandi, possono richiedere file modello aggiuntivi o versioni compatibili di Python/CUDA. L'architettura e pronta per queste integrazioni senza dover modificare il resto della pipeline.

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
  cli.py              entrypoint CLI
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

## Annotazione Prosodica

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

## Quick Start Con Make

Il modo piu semplice per preparare e usare Poetry Voice e tramite `make`.

Prerequisiti:

- Docker;
- Docker Compose;
- `make`;
- driver NVIDIA installato sull'host;
- NVIDIA Container Toolkit installato.

Setup completo:

```bash
make setup
```

Questo comando:

1. crea `config.yaml` da `config.example.yaml`, se non esiste;
2. crea le directory `outputs`, `uploads`, `models/piper` e `ollama`;
3. costruisce l'immagine Docker;
4. scarica il modello LLM Ollama configurato;
5. scarica la voce Piper italiana configurata.

Avvio dell'app:

```bash
make up
```

Apri:

```text
http://localhost:8000
```

Fermare tutto:

```bash
make down
```

Vedere i log:

```bash
make logs
```

Verificare la GPU:

```bash
make gpu-check
```

## Comandi Make Disponibili

| Comando | Descrizione |
| --- | --- |
| `make setup` | Prepara config, directory, immagine Docker e modelli |
| `make init` | Crea config e directory locali |
| `make build` | Ricostruisce l'immagine Docker |
| `make up` | Avvia web app e Ollama |
| `make down` | Ferma i container |
| `make restart` | Riavvia il servizio |
| `make logs` | Mostra i log del servizio |
| `make shell` | Apre una shell nel container |
| `make gpu-check` | Esegue `nvidia-smi` nel container |
| `make pull-models` | Scarica/aggiorna modello Ollama e voce Piper |
| `make cli ARGS='--help'` | Esegue la CLI nel container |
| `make convert INPUT=uploads/poesia.txt` | Converte una poesia da CLI |
| `make test` | Esegue i test nel container |
| `make lint` | Esegue Ruff e Black check nel container |
| `make clean` | Pulisce `outputs/` e `uploads/`, mantenendo i modelli |

Esempi CLI:

```bash
make cli ARGS="--help"
make convert INPUT=uploads/poesia.txt
make convert INPUT=uploads/poesia.txt ARGS="--format flac"
make convert INPUT=uploads/poesia.pdf ARGS="--voice piper"
```

I file da convertire possono essere copiati in `uploads/`, che viene montata nel container.

## Quick Start Con Docker Compose

Se preferisci usare Docker Compose direttamente, puoi evitare `make`.

Prerequisiti:

- Docker;
- Docker Compose;
- driver NVIDIA installato sull'host;
- NVIDIA Container Toolkit installato.

Crea la configurazione locale:

```bash
cp config.example.yaml config.yaml
```

Costruisci e avvia:

```bash
docker compose up --build
```

Apri l'interfaccia web:

```text
http://localhost:8000
```

Anche l'API Ollama viene esposta:

```text
http://localhost:11434
```

## Cosa Succede Al Primo Avvio

Il container e autocontenuto:

1. Avvia Ollama dentro il container.
2. Attende che Ollama sia pronto.
3. Scarica il modello configurato da `OLLAMA_MODEL`.
4. Avvia l'app web FastAPI di Poetry Voice.

Valori predefiniti:

```yaml
OLLAMA_MODEL: qwen3:8b
POETRYVOICE_PULL_MODEL: "1"
```

Il primo avvio puo richiedere tempo perche viene scaricato il modello LLM. Il modello viene salvato in modo persistente in:

```text
./ollama
```

Le cache relative a TTS e Hugging Face vengono salvate in:

```text
./models
```

I file audio generati vengono scritti in:

```text
./outputs
```

I file caricati dall'interfaccia web vengono scritti in:

```text
./uploads
```

Dopo il primo download, gli avvii successivi sono piu rapidi perche il modello e gia in cache.

## Evitare Il Download Del Modello A Ogni Avvio

Imposta questo valore in `docker-compose.yml`:

```yaml
environment:
  POETRYVOICE_PULL_MODEL: "0"
```

Puoi comunque scaricare manualmente un modello:

```bash
docker compose exec poetry-voice ollama pull qwen3:8b
```

## Scegliere Il Modello

Modifica `docker-compose.yml`:

```yaml
environment:
  OLLAMA_MODEL: qwen3:8b
```

E mantieni allineato `config.yaml`:

```yaml
llm:
  provider: ollama
  model: qwen3:8b
  base_url: http://localhost:11434
```

Con GPU da 12 GB e consigliabile usare modelli compatti. Con GPU da 24 GB c'e piu margine per LLM piu grandi e motori TTS piu pesanti.

## Verifica GPU

Esegui:

```bash
make gpu-check
```

Se il comando fallisce, il problema di solito e nella configurazione del driver NVIDIA sull'host o del NVIDIA Container Toolkit.

## Uso Dell'Interfaccia Web

La UI web supporta:

- upload della poesia;
- scelta del motore TTS;
- scelta della lingua;
- scelta del tono di lettura;
- scelta della velocita di lettura;
- editor dell'anteprima annotata per modificare versi, pause ed emozioni;
- aggiunta o rimozione di versi prima della rigenerazione;
- scelta del provider LLM;
- scelta del modello LLM;
- anteprima annotata;
- log di avanzamento durante analisi, sintesi e post-processing;
- ascolto audio;
- download audio.

Flusso consigliato:

1. Carica un file e genera il primo audiolibro.
2. Dopo il risultato, usa l'anteprima annotata come editor.
3. Nell'anteprima puoi modificare direttamente ogni verso, la pausa dopo il verso e l'emozione.
4. Puoi anche eliminare un verso o aggiungerne uno nuovo sotto quello corrente.
5. Usa `Rigenera da anteprima modificata` per sintetizzare di nuovo senza rifare l'analisi LLM.
6. Usa `Genera audiolibro` per rifare invece l'analisi partendo dal testo sorgente estratto.

Esempi di indicazioni utili:

```text
Allunga la pausa dopo il secondo verso.
Leggi la prima strofa in modo piu sospeso.
Rendi l'ultimo verso piu intimo, senza teatralita.
Mantieni un ritmo lento ma non monotono.
```

Scelte di accessibilita:

- testo grande;
- alto contrasto;
- focus da tastiera ben visibile;
- controlli form nativi;
- HTML semantico;
- label esplicite e struttura compatibile con screen reader;
- controlli audio standard del browser.

## Uso Da CLI

Metodo consigliato con Make:

```bash
make convert INPUT=uploads/input.txt
make convert INPUT=uploads/input.pdf
make convert INPUT=uploads/input.md
```

Con opzioni:

```bash
make convert INPUT=uploads/input.txt ARGS="--voice piper"
make convert INPUT=uploads/input.txt ARGS="--speaker it_IT-paola-medium"
make convert INPUT=uploads/input.txt ARGS="--emotion auto"
make convert INPUT=uploads/input.txt ARGS="--speed slow"
make convert INPUT=uploads/input.txt ARGS="--tone malinconico"
make convert INPUT=uploads/input.txt ARGS="--language it"
make convert INPUT=uploads/input.txt ARGS="--format flac"
```

Oppure direttamente con Docker Compose:

```bash
docker compose exec poetry-voice poetryvoice input.txt
docker compose exec poetry-voice poetryvoice input.pdf
docker compose exec poetry-voice poetryvoice input.md
```

Con opzioni:

```bash
docker compose exec poetry-voice poetryvoice input.txt --voice kokoro
docker compose exec poetry-voice poetryvoice input.txt --voice dia
docker compose exec poetry-voice poetryvoice input.txt --speaker it_IT-paola-medium
docker compose exec poetry-voice poetryvoice input.txt --emotion auto
docker compose exec poetry-voice poetryvoice input.txt --speed slow
docker compose exec poetry-voice poetryvoice input.txt --tone caldo
docker compose exec poetry-voice poetryvoice input.txt --language it
docker compose exec poetry-voice poetryvoice convert input.txt --format flac
```

Poiche il compose monta i volumi locali, i file generati restano disponibili sull'host in `./outputs`.

## Configurazione

Esempio:

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

## Parser Supportati

| Formato | Estensione | Implementazione |
| --- | --- | --- |
| Testo semplice | `.txt` | lettura UTF-8 |
| Markdown | `.md`, `.markdown` | `markdown-it-py` |
| PDF | `.pdf` | estrazione layout con `pypdf` |

## Provider LLM

Il layer LLM e astratto. Le modalita attuali sono:

- `ollama`;
- `openai`;
- `generic`.

Ollama e il provider predefinito e gira dentro il container Docker.

Il provider riceve la poesia e restituisce un modello `PoemAnnotation` validato. Se durante lo sviluppo la chiamata al LLM fallisce, un fallback euristico puo generare un'annotazione base per mantenere testabile il resto della pipeline.

## Motori TTS

Il layer TTS e astratto. Gli adapter attuali sono:

- `kokoro`;
- `dia`;
- `xtts`;
- `piper`.

Il motore selezionato si configura solo via YAML:

```yaml
tts:
  engine: piper
```

Il modello Piper fornito come default e italiano (`it_IT-paola-medium`). Se selezioni un'altra lingua nella UI o da CLI, devi configurare anche una voce TTS coerente con quella lingua, altrimenti la sintesi usera comunque il modello vocale italiano.

Le voci sono legate al motore TTS. `Paola` e `Riccardo` sono voci Piper: la UI le mostra solo quando il motore selezionato e `Piper`, e il backend rifiuta combinazioni incompatibili invece di usare silenziosamente il fallback.

### Voci Piper

La voce Piper predefinita e:

```yaml
tts:
  speaker: it_IT-paola-medium
  model_path: /models/piper/it_IT-paola-medium.onnx
```

La UI mostra le voci italiane registrate nel catalogo interno:

| Voce | Chiave | Note |
| --- | --- | --- |
| Paola | `it_IT-paola-medium` | qualita media, default consigliato |
| Riccardo | `it_IT-riccardo-x_low` | molto leggero, qualita inferiore |

Se il modello non e presente, Poetry Voice lo scarica automaticamente a runtime e lo salva in:

```text
./models/piper/
```

Lo stesso vale dalla CLI:

```bash
make convert INPUT=uploads/poesia.txt ARGS="--voice piper --speaker it_IT-paola-medium"
make convert INPUT=uploads/poesia.txt ARGS="--voice piper --speaker it_IT-riccardo-x_low"
```

Per aggiungere altre voci Piper, registra la voce in `poetry_voice/tts/piper_voices.py` con chiave, lingua, percorso locale, URL `.onnx` e URL `.onnx.json`. Dopo questo la voce puo essere esposta nella UI e scaricata automaticamente come Paola.

Il build Docker installa sempre l'applicazione core. I pacchetti TTS pesanti opzionali vengono tentati con:

```yaml
build:
  args:
    INSTALL_HEAVY_TTS: "1"
```

Se un backend opzionale non e disponibile per l'ambiente Python/CUDA corrente, il container parte comunque e Poetry Voice usa `espeak-ng` come fallback vocale in italiano. Questo mantiene utilizzabili pipeline, UI e post-processing mentre installi o configuri il motore desiderato. Nei log del container viene indicato quando un motore reale non parte e viene usato il fallback.

## Post-Processing Audio

FFmpeg viene usato per:

- normalizzazione LUFS;
- compressione leggera;
- breve fade-in;
- esportazione MP3/FLAC/WAV/OGG;
- bitrate configurabile.

## Sviluppo

Con container:

```bash
make test
make lint
make shell
```

Setup locale:

```bash
python3.12 -m venv .venv
source .venv/bin/activate
pip install -e ".[dev,tts]"
cp config.example.yaml config.yaml
```

Controlli qualita:

```bash
ruff check .
black --check .
pytest
```

## Aggiungere Un Nuovo Provider LLM

1. Crea una classe che implementa `LLMProvider`.
2. Restituisci un `PoemAnnotation` validato.
3. Registra la classe in `poetry_voice/llm/factory.py`.
4. Aggiungi il valore di configurazione in `LLMConfig.provider`.

## Aggiungere Un Nuovo Motore TTS

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
