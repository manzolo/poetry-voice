# Poetry Voice — Uso con Docker e GPU NVIDIA

Questa via offre la qualita massima: tutto gira dentro un container, **Ollama
incluso**, con accelerazione sulla GPU NVIDIA. Non devi installare Python ne le
dipendenze sul tuo sistema.

Se non hai una GPU NVIDIA, usa invece la [versione standalone](standalone.md).

## Prerequisiti

- Docker
- Docker Compose
- `make`
- driver NVIDIA installato sull'host
- NVIDIA Container Toolkit installato

## Avvio in due comandi

```bash
make setup
make up
```

Poi apri:

```text
http://localhost:8000
```

Anche l'API di Ollama viene esposta:

```text
http://localhost:11434
```

Per fermare tutto:

```bash
make down
```

### Cosa fa `make setup`

1. crea `config.yaml` da `config.example.yaml`, se non esiste;
2. crea le directory `outputs`, `uploads`, `models/piper` e `ollama`;
3. costruisce l'immagine Docker;
4. scarica il modello LLM Ollama configurato;
5. scarica la voce Piper italiana configurata.

## Comandi make disponibili

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

I file da convertire vanno copiati in `uploads/`, montata nel container.

## Cosa succede al primo avvio

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

Il primo avvio puo richiedere tempo perche viene scaricato il modello LLM. Il
modello resta salvato in `./ollama`. Le cache TTS e Hugging Face vanno in
`./models`. Gli audio generati in `./outputs`, i file caricati in `./uploads`.

## Evitare il download del modello a ogni avvio

In `docker-compose.yml`:

```yaml
environment:
  POETRYVOICE_PULL_MODEL: "0"
```

Puoi comunque scaricarlo a mano:

```bash
docker compose exec poetry-voice ollama pull qwen3:8b
```

## Scegliere il modello

In `docker-compose.yml`:

```yaml
environment:
  OLLAMA_MODEL: qwen3:8b
```

E allinea `config.yaml`:

```yaml
llm:
  provider: ollama
  model: qwen3:8b
  base_url: http://localhost:11434
```

Con GPU da 12 GB conviene usare modelli compatti. Con 24 GB c'e margine per LLM
piu grandi e motori TTS piu pesanti.

## Verifica GPU

```bash
make gpu-check
```

Se fallisce, il problema e di solito nel driver NVIDIA dell'host o nel NVIDIA
Container Toolkit.

## Senza make (Docker Compose diretto)

```bash
cp config.example.yaml config.yaml
docker compose up --build
```

## Motori TTS pesanti opzionali

Il build installa sempre l'app core. I pacchetti TTS neurali pesanti sono
tentati con:

```yaml
build:
  args:
    INSTALL_HEAVY_TTS: "1"
```

Se un backend opzionale non e disponibile per l'ambiente Python/CUDA corrente,
il container parte comunque e Poetry Voice usa `espeak-ng` come voce di
ripiego. I log indicano quando un motore reale non parte e si usa il ripiego.

Per la versione senza Docker e senza GPU, vedi [standalone.md](standalone.md).
