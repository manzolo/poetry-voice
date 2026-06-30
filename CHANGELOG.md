# Changelog

Tutte le modifiche rilevanti a questo progetto sono documentate in questo file.

Il formato si basa su [Keep a Changelog](https://keepachangelog.com/it/1.1.0/)
e il progetto segue il [versionamento semantico](https://semver.org/lang/it/).

## [Unreleased]

### Aggiunto
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
- Anteprima annotata allineata e resa a "card".
- Action della CI aggiornati a Node 24 (checkout@v7, setup-python@v6, cache@v6).

### Corretto
- CI verde: lint (ruff/black) puliti e test resi offline e deterministici.

## [0.1.0] - 2026-06-30

### Aggiunto
- Prima versione: pipeline parser → analisi LLM → annotazione prosodica → motore
  TTS → post-processing FFmpeg, con CLI, interfaccia web FastAPI accessibile e
  runtime Docker con GPU NVIDIA e Ollama incluso.
