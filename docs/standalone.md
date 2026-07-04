# Poetry Voice — Uso standalone (senza Docker, senza GPU)

Questa e la via piu semplice: Poetry Voice gira direttamente sul tuo computer,
usando la CPU. Non servono Docker ne una scheda video NVIDIA.

I comandi qui sotto sono pensati per essere pochi e da copiare con un solo clic
(su GitHub ogni blocco di codice ha il pulsante per copiarlo). Quando puoi, ti
basta **un comando solo**.

## In un comando solo

Se non hai ancora il progetto:

```bash
git clone https://github.com/manzolo/poetry-voice.git && cd poetry-voice
```

Poi, dalla cartella del progetto:

```bash
make local
```

Questo installa tutto la prima volta e poi avvia l'applicazione. Quando vedi che
e pronta, apri il browser su:

```text
http://127.0.0.1:8000
```

Per fermarla: premi `Ctrl` + `C` nel terminale.
Per riavviarla in futuro, di nuovo `make local`.

## Prerequisiti

- **Python 3.12 o superiore** (verifica con `python3 --version`).
- **make** (su Ubuntu/Debian e nel pacchetto omonimo).
- **ffmpeg** (serve per MP3, FLAC e OGG).
- **espeak-ng** (facoltativo: voce di ripiego se Piper non e disponibile).

Su Ubuntu/Debian, un comando solo li installa tutti:

```bash
sudo apt install make ffmpeg espeak-ng
```

## Se preferisci due passi separati

```bash
make local-setup    # installa l'app e la voce Piper (una volta sola)
make local-run      # avvia la web app
```

## Convertire una poesia da terminale

`INPUT` puo essere un file in qualsiasi cartella leggibile:

```bash
make local-convert INPUT=poesia.txt
```

Con opzioni (formato, velocita, tono):

```bash
make local-convert INPUT=poesia.txt ARGS="--format flac"
make local-convert INPUT=poesia.txt ARGS="--speed slow --tone caldo"
```

L'audio finale viene scritto in `local-data/outputs/`.

## Qualita della lettura

- La voce predefinita e **Piper** (italiano, "Paola"), che gira bene su CPU.
- L'analisi della poesia usa un modello linguistico (LLM). Senza un LLM attivo,
  Poetry Voice usa un **analizzatore di ripiego** integrato: funziona, ma le
  pause e le emozioni sono piu semplici.
- Per la qualita migliore puoi installare [Ollama](https://ollama.com) sul tuo
  computer e scaricare un modello:

  ```bash
  ollama pull qwen3:8b
  ```

  Poetry Voice lo usa in automatico se e in ascolto su `http://localhost:11434`.

## Dove finiscono i file

Il modo locale tiene tutto sotto `local-data/`, una cartella di tua proprieta,
separata da quelle che usa Docker (create come root). Cosi non serve mai `sudo`.

| Cartella | Contenuto |
| --- | --- |
| `local-data/outputs/` | gli audiolibri generati |
| `local-data/uploads/` | i file caricati dalla web app |
| `local-data/models/piper/` | le voci Piper scaricate |

## Test e qualita del codice (per chi sviluppa)

```bash
make local-test     # esegue i test
make local-lint     # esegue ruff e black --check
```

## Risoluzione problemi

- **"Serve Python >= 3.12"**: indica un Python piu recente, per esempio
  `make local-setup PYTHON=python3.12`.
- **MP3 non generato / errore ffmpeg**: installa ffmpeg
  (`sudo apt install ffmpeg`). In alternativa usa `ARGS="--format wav"`.
- **Voce robotica o "ronzio"**: significa che Piper non era disponibile ed e
  stato usato il ripiego. Controlla che `piper-tts` sia installato; in caso,
  rilancia `make local-setup`.
- **Porta gia occupata**: cambia porta, ad esempio `make local-run PORT=8010`.
- **"Permission denied" su `uploads/` o `outputs/`**: stai usando le vecchie
  cartelle create da Docker (di proprieta di root). Il modo locale usa invece
  `local-data/`; se vuoi riprenderti le cartelle Docker:

  ```bash
  make fix-perms
  ```

Per la versione con Docker e GPU NVIDIA, vedi [docker.md](docker.md).
