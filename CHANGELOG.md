# Changelog

Tutte le modifiche rilevanti a questo progetto sono documentate in questo file.

Il formato si basa su [Keep a Changelog](https://keepachangelog.com/it/1.1.0/)
e il progetto segue il [versionamento semantico](https://semver.org/lang/it/).

## [Unreleased]

### Aggiunto
- Suddivisione del testo configurabile: **per versi** (a capo, default) o
  **per frasi** in base alla punteggiatura (per la prosa: gli a capo interni
  ai paragrafi vengono uniti, i paragrafi restano separatori di strofa).
  Disponibile nella UI, da CLI (`--split lines|sentences`) e in config
  (`pipeline.segmentation`).
- UI: sorgente del testo a scelta tra upload file e area di testo per scrivere
  o incollare la poesia direttamente (interruttore accessibile con radio).
- UI: pulsante **Ferma elaborazione** per annullare un job in corso (endpoint
  `POST /jobs/{id}/cancel`, stato `cancelled`); durante l'elaborazione i campi
  parametri scompaiono e resta solo l'avanzamento con il pulsante di stop, poi
  ricompaiono a fine lavoro, su errore o annullamento.
- UI: il campo "Modello LLM" propone in tendina i modelli gia scaricati
  nell'istanza Ollama configurata (endpoint `GET /ollama-models`), restando
  comunque scrivibile a mano.
- UI: pulsante **Layout compatto** (il layout accessibile resta il default):
  resa piu densa con campi su due colonne, scelta ricordata dal browser,
  contrasto e focus invariati.
- Interfaccia web bilingue italiano/inglese: selettore accessibile in alto,
  scelta ricordata con un cookie (`?lang=it|en`), stringhe in `ui/i18n.py` con
  test di parita' delle traduzioni. I log di avanzamento della pipeline
  restano per ora in italiano.
- Voci inglesi a catalogo: Lessac e Ryan (Piper, `en_US-*`), Heart e Michael
  (Kokoro, `af_heart`/`am_michael`). Le voci sono ora legate anche alla lingua:
  la UI filtra l'elenco per motore + lingua di lettura, il backend rifiuta gli
  abbinamenti sbagliati e da CLI `--language en` senza `--speaker` sceglie da
  solo una voce adatta.
- `README.en.md`: versione inglese del README, con link incrociati.
- Screenshot della UI (form principale e anteprima annotata) nei README, con
  alt text descrittivi, sotto `docs/img/`.
- Analisi LLM a blocchi di strofe per i testi lunghi (soglia configurabile con
  `llm.max_lines_per_chunk`, default 24): una passata leggera ricava titolo e
  tono globale, poi ogni blocco viene annotato con quel contesto e ricomposto
  per numero di verso.
- Finestra di contesto Ollama configurabile (`llm.num_ctx`, default 8192): i
  default del server (2048-4096 token) troncavano i testi lunghi in silenzio.
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
- README piu snello: in vista restano identita del progetto, screenshot,
  prerequisiti e avvio (ora con `git clone` e comando apt per Python/make/
  ffmpeg); architettura, configurazione, voci, sviluppo e roadmap sono
  sezioni richiudibili (`<details>`). Prerequisiti e clone aggiunti anche
  alle guide `docs/standalone.md` e `docs/docker.md`.
- UI: suggerimento sotto "Lingua di lettura" per chiarire che e la lingua
  della poesia (e determina le voci disponibili), distinta dalla lingua
  dell'interfaccia in alto a destra.
- Il fallback dell'analisi LLM non e piu silenzioso: log espliciti quando
  l'intera analisi, un singolo blocco o un singolo verso degradano
  sull'euristica, e quando l'LLM restituisce indici duplicati o inesistenti.
- Le voci mostrate nella UI e la validazione derivano da un unico catalogo
  (`piper_voices.py` + `kokoro_voices.py`): per aggiungere una voce basta
  editare un solo file.
- Extra di installazione TTS separati in `kokoro` / `xtts` / `piper`, cosi un
  motore fragile (es. coqui/xtts) non blocca l'installazione degli altri.
- Anteprima annotata allineata e resa a "card".
- Action della CI aggiornati a Node 24 (checkout@v7, setup-python@v6, cache@v6).

### Corretto
- UI: nel layout compatto i campi parametri restavano visibili durante
  l'elaborazione (il `display: grid` della griglia vinceva sull'attributo
  `hidden`); ora una regola globale `[hidden] { display: none !important; }`
  garantisce che cio che e nascosto sparisca davvero.
- Kokoro: il `lang_code` deriva dal prefisso della voce (`if_sara` → `i`,
  `af_heart` → `a`) invece che da `language[:1]`, che funzionava solo per
  l'italiano.
- Niente piu versi ripetuti o inventati negli audio lunghi: l'LLM non rigenera
  piu il testo della poesia. Riceve i versi numerati e restituisce solo
  annotazioni indicizzate (`"line": N`) che vengono riattaccate al testo del
  file originale: il TTS legge per costruzione i versi veri.
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
