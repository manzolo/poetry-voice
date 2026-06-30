# Changelog

Tutte le modifiche rilevanti a questo progetto sono documentate in questo file.

Il formato si basa su [Keep a Changelog](https://keepachangelog.com/it/1.1.0/)
e il progetto segue il [versionamento semantico](https://semver.org/lang/it/).

## [Unreleased]

### Aggiunto
- Clonazione voce con **XTTS v2**: campo `speaker_wav` nella config, opzione CLI
  `--speaker-wav` e upload del campione nella UI (salvato in
  `uploads/voci-clonate/`); usa il fork `coqui-tts[codec]` con `transformers`
  pinnato a 4.x. L'import dello stack e verificato; la sintesi XTTS reale non e
  ancora confermata (errore a runtime nella chiamata di sintesi, da debuggare
  preferibilmente su GPU — vedi BACKLOG). Kokoro resta l'opzione neurale
  verificata end-to-end.
- Motore TTS **Kokoro** (neurale) con voci italiane Sara (`if_sara`) e Nicola
  (`im_nicola`); rispetta le pause per verso ed espone le voci nella UI. Richiede
  lo stack neurale (Docker, oppure Python ≤ 3.13 + espeak-ng): i wheel di
  spacy/kokoro non sono disponibili per Python 3.14.
- Esecuzione standalone su CPU senza Docker e senza GPU: target `make local`,
  `make local-setup`, `make local-run`, `make local-convert`.
- Dati locali sotto `local-data/` (di proprieta dell'utente) e target
  `make fix-perms` per riprendersi le cartelle create da Docker come root.
- `make up` e `make local-run` stampano la URL da aprire nel browser.
- Anteprima annotata: riordino dei versi (su/giu).
- Barra di avanzamento accessibile durante l'elaborazione.
- CI GitHub Actions: lint, test e una conversione di prova su CPU con Piper.
- Documentazione divisa: README hub + `docs/docker.md` + `docs/standalone.md`.
- `BACKLOG.md` e `LICENSE` (MIT).

### Modificato
- Le voci mostrate nella UI e la validazione derivano da un unico catalogo
  (`piper_voices.py` + `kokoro_voices.py`): per aggiungere una voce basta
  editare un solo file.
- Extra di installazione TTS separati in `kokoro` / `xtts` / `piper`, cosi un
  motore fragile (es. coqui/xtts) non blocca l'installazione degli altri.
- Anteprima annotata allineata e resa a "card".
- Action della CI aggiornati a Node 24 (checkout@v7, setup-python@v6, cache@v6).

### Corretto
- Piper ora rispetta `pause_before`/`pause_after` per ogni verso: la sintesi
  avviene verso per verso e i silenzi vengono inseriti con durata esatta. Prima
  il valore "pausa dopo" dell'anteprima veniva ignorato (Piper usava solo un
  silenzio globale).
- CI verde: lint (ruff/black) puliti e test resi offline e deterministici.

## [0.1.0] - 2026-06-30

### Aggiunto
- Prima versione: pipeline parser → analisi LLM → annotazione prosodica → motore
  TTS → post-processing FFmpeg, con CLI, interfaccia web FastAPI accessibile e
  runtime Docker con GPU NVIDIA e Ollama incluso.
