SHELL := /usr/bin/env bash

COMPOSE ?= docker compose
SERVICE ?= poetry-voice
CONFIG ?= config.yaml
EXAMPLE_CONFIG ?= config.example.yaml

.DEFAULT_GOAL := help

.PHONY: help setup init build up down restart logs shell cli convert pull-models gpu-check test lint clean

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
	@printf "\nManutenzione:\n"
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
	@find outputs uploads -mindepth 1 -maxdepth 1 -exec rm -rf {} +
	@printf "Puliti outputs/ e uploads/. Modelli e cache mantenuti.\n"
