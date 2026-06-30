SHELL := /usr/bin/env bash

COMPOSE ?= docker compose
SERVICE ?= poetry-voice
CONFIG ?= config.yaml
EXAMPLE_CONFIG ?= config.example.yaml

# --- Esecuzione locale senza Docker e senza GPU (TTS Piper su CPU) ---
VENV ?= .venv
PYTHON ?= python3
HOST ?= 127.0.0.1
PORT ?= 8000
# I dati locali stanno sotto local-data/ (di proprieta dell'utente), separati
# dalle cartelle usate da Docker che il container crea come root.
LOCAL_DATA ?= $(CURDIR)/local-data
LOCAL_CONFIG ?= config.local.yaml
PIPER_MODELS_DIR ?= $(LOCAL_DATA)/models/piper
LOCAL_ENV := PATH="$(CURDIR)/$(VENV)/bin:$$PATH" POETRYVOICE_CONFIG="$(LOCAL_CONFIG)" POETRYVOICE_UPLOAD_DIR="$(LOCAL_DATA)/uploads" PIPER_MODELS_DIR="$(PIPER_MODELS_DIR)"

.DEFAULT_GOAL := help

.PHONY: help setup init build up down restart logs shell cli convert pull-models gpu-check test lint clean \
        fix-perms local local-check local-setup local-run local-convert local-test local-lint

help:
	@printf "Poetry Voice\n\n"
	@printf "Comandi principali:\n"
	@printf "  make setup        Prepara config, directory, build immagine e scarica modelli\n"
	@printf "  make up           Avvia web app e Ollama\n"
	@printf "  make down         Ferma i container\n"
	@printf "  make logs         Mostra i log\n"
	@printf "  make shell        Apre una shell nel container\n"
	@printf "  make gpu-check    Verifica accesso GPU NVIDIA\n"
	@printf "\nUso CLI:\n"
	@printf "  make cli ARGS='--help'\n"
	@printf "  make convert INPUT=uploads/poesia.txt\n"
	@printf "  make convert INPUT=uploads/poesia.txt ARGS='--format flac'\n"
	@printf "\nSenza Docker / senza GPU (Piper su CPU):\n"
	@printf "  make local        Installa e avvia tutto con un comando solo\n"
	@printf "  make local-setup  Solo installazione (crea venv, installa app e Piper)\n"
	@printf "  make local-run    Solo avvio della web app su http://%s:%s\n" "$(HOST)" "$(PORT)"
	@printf "  make local-convert INPUT=poesia.txt   Converte da CLI in locale\n"
	@printf "\nManutenzione:\n"
	@printf "  make fix-perms    Riassegna all'utente i permessi delle cartelle dati (usa sudo)\n"
	@printf "  make build        Ricostruisce l'immagine\n"
	@printf "  make pull-models  Scarica/aggiorna modelli Ollama e Piper\n"
	@printf "  make test         Esegue pytest nel container\n"
	@printf "  make lint         Esegue ruff e black --check nel container\n"
	@printf "  make clean        Rimuove output/upload generati, mantiene modelli e cache\n"

setup: init build pull-models

init:
	@if [ ! -f "$(CONFIG)" ]; then cp "$(EXAMPLE_CONFIG)" "$(CONFIG)"; fi
	@mkdir -p outputs uploads models/piper ollama
	@printf "Setup directory completato.\n"

build: init
	$(COMPOSE) build

up: init
	@printf "\n>>> Avvio dei container. Quando e pronto, apri nel browser:\n>>>     http://localhost:8000\n\n"
	$(COMPOSE) up

down:
	$(COMPOSE) down

restart: down up

logs:
	$(COMPOSE) logs -f $(SERVICE)

shell:
	$(COMPOSE) exec $(SERVICE) bash

cli:
	$(COMPOSE) exec $(SERVICE) poetryvoice $(ARGS)

convert:
	@if [ -z "$(INPUT)" ]; then printf "Errore: usa make convert INPUT=uploads/poesia.txt\n" >&2; exit 1; fi
	$(COMPOSE) exec $(SERVICE) poetryvoice $(INPUT) $(ARGS)

pull-models: init
	$(COMPOSE) run --rm $(SERVICE) bash -lc 'ollama serve >/tmp/ollama.log 2>&1 & until ollama list >/dev/null 2>&1; do sleep 1; done; ollama pull "$${OLLAMA_MODEL:-qwen3:8b}"; mkdir -p "$$(dirname "$${PIPER_MODEL_PATH:-/models/piper/it_IT-paola-medium.onnx}")"; curl -L --fail --output "$${PIPER_MODEL_PATH:-/models/piper/it_IT-paola-medium.onnx}" "$${PIPER_MODEL_URL}"; curl -L --fail --output "$${PIPER_MODEL_PATH:-/models/piper/it_IT-paola-medium.onnx}.json" "$${PIPER_CONFIG_URL}"'

gpu-check:
	$(COMPOSE) run --rm $(SERVICE) nvidia-smi

test:
	$(COMPOSE) run --rm $(SERVICE) pytest

lint:
	$(COMPOSE) run --rm $(SERVICE) bash -lc 'ruff check . && black --check .'

clean:
	@find outputs uploads -mindepth 1 -maxdepth 1 -exec rm -rf {} + 2>/dev/null || true
	@find "$(LOCAL_DATA)/outputs" "$(LOCAL_DATA)/uploads" -mindepth 1 -maxdepth 1 -exec rm -rf {} + 2>/dev/null || true
	@printf "Puliti outputs/ e uploads/ (Docker e locale). Modelli e cache mantenuti.\n"

# Riassegna all'utente corrente la proprieta delle cartelle dati. Utile quando
# i container Docker (che girano come root) hanno creato file non scrivibili.
# Richiede sudo. Le cartelle locali create da "make local-*" sono gia tue.
fix-perms:
	@for d in outputs uploads models ollama "$(LOCAL_DATA)"; do \
		if [ -e "$$d" ]; then sudo chown -R "$$(id -u):$$(id -g)" "$$d"; fi; \
	done
	@printf "Permessi delle cartelle dati riassegnati a %s.\n" "$$(id -un)"

# --- Target per l'esecuzione locale senza Docker e senza GPU ---

# Un comando solo: installa (se serve) e avvia la web app.
local: local-setup local-run

local-check:
	@command -v ffmpeg >/dev/null 2>&1 || printf "ATTENZIONE: ffmpeg non trovato. Per MP3/FLAC/OGG installalo: sudo apt install ffmpeg\n"
	@command -v espeak-ng >/dev/null 2>&1 || printf "Nota: espeak-ng non trovato, usato solo come voce di fallback. Opzionale: sudo apt install espeak-ng\n"

local-setup: local-check
	@$(PYTHON) -c 'import sys; raise SystemExit(0 if sys.version_info >= (3, 12) else "Serve Python >= 3.12 (override con: make local-setup PYTHON=python3.12)")'
	@test -d "$(VENV)" || $(PYTHON) -m venv "$(VENV)"
	$(VENV)/bin/pip install --upgrade pip
	$(VENV)/bin/pip install -e ".[dev]"
	@$(VENV)/bin/pip install piper-tts || printf "\nNota: piper-tts non installato (wheel non disponibile per questo Python). L'app usera la voce di fallback espeak-ng.\n"
	@mkdir -p "$(LOCAL_DATA)/uploads" "$(LOCAL_DATA)/outputs" "$(PIPER_MODELS_DIR)"
	@printf "\nSetup locale completato. Avvia con:  make local-run\n"
	@printf "Senza Ollama attivo l'analisi usa il fallback euristico (qualita inferiore).\n"

local-run: local-check
	@printf "\n>>> Poetry Voice e in avvio. Apri nel browser:\n>>>     http://%s:%s\n>>> (premi Ctrl+C per fermare)\n\n" "$(HOST)" "$(PORT)"
	$(LOCAL_ENV) $(VENV)/bin/poetryvoice web --host $(HOST) --port $(PORT)

local-convert: local-check
	@if [ -z "$(INPUT)" ]; then printf "Errore: usa make local-convert INPUT=poesia.txt\n" >&2; exit 1; fi
	$(LOCAL_ENV) $(VENV)/bin/poetryvoice $(INPUT) $(ARGS)

local-test:
	$(VENV)/bin/pytest

local-lint:
	$(VENV)/bin/ruff check . && $(VENV)/bin/black --check .
