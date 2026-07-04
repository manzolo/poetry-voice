# Backlog

Elenco di lavoro svolto e idee da affrontare. Niente date rigide: una traccia
condivisa per non perdere le cose.

## Fatto

- [x] Messo il progetto su git e su GitHub (repo pubblico, licenza MIT).
- [x] README ispirato a Massimo Bianchini, con il caso d'uso di supporto a chi
      non vede per l'ascolto di poesie e testi.
- [x] UI: anteprima annotata allineata e resa a "card".
- [x] UI: riordino dei versi (su/giu) oltre ad aggiungi/elimina.
- [x] UI: barra di avanzamento accessibile durante l'elaborazione.
- [x] Esecuzione standalone su CPU senza Docker e senza GPU (`make local`).
- [x] Dati locali sotto `local-data/` di proprieta dell'utente (niente conflitti
      con i file root creati da Docker); target `make fix-perms`.
- [x] `make up` e `make local-run` stampano la URL da aprire.
- [x] CI GitHub Actions: lint, test e conversione di prova su CPU; action su Node 24.
- [x] Fix allucinazioni sui testi lunghi: l'LLM non rigenera piu il testo dei
      versi (annotazioni indicizzate per numero, riattaccate al testo
      originale), `num_ctx` Ollama configurabile, analisi a blocchi di strofe
      (`max_lines_per_chunk`), fallback loggati e mai silenziosi.
- [x] UI bilingue italiano/inglese (`ui/i18n.py`, `?lang=` + cookie, test di
      parita' delle traduzioni) e `README.en.md` con link incrociati.
- [x] Voci inglesi a catalogo (Piper: Lessac/Ryan; Kokoro: Heart/Michael),
      voci legate a motore+lingua, CLI `--language` che auto-sceglie la voce,
      fix `lang_code` Kokoro dal prefisso della voce.
- [x] UI: sorgente del testo a scelta tra upload e textarea.
- [x] UI: pulsante "Ferma elaborazione" (`POST /jobs/{id}/cancel`) e parametri
      nascosti durante l'elaborazione (solo avanzamento + stop).
- [x] UI: campo modello LLM con tendina dei modelli presenti in Ollama
      (`GET /ollama-models`), sempre editabile a mano.
- [x] UI: layout compatto opzionale (l'accessibile resta il default).
- [x] Suddivisione del testo per versi (default) o per frasi in base alla
      punteggiatura (`pipeline.segmentation`, UI + CLI `--split`).
- [x] Test per le route della UI (index, convert, cancel, ollama-models, i18n).

## Da fare / idee

### Accessibilita (priorita alta)
- [ ] Aggiungere una favicon (ora `/favicon.ico` da 404 nei log).
- [ ] Test di accessibilita con screen reader reali (NVDA/VoiceOver).
- [ ] Verificare la barra di avanzamento e il riordino versi con sola tastiera.

### Qualita audio / TTS
- [ ] XTTS v2: la sintesi reale non parte ancora. Dipendenze RISOLTE
      (`coqui-tts[codec]` + `transformers>=4.40,<5`): l'import ora funziona.
      Resta un errore a runtime nella chiamata di sintesi (`tts.tts(...)` lancia
      un'eccezione con messaggio vuoto → fallback). Prossimo passo: ottenere il
      traceback completo (loggare l'eccezione, non solo `str(exc)`) e provare su
      GPU. Wiring completo: engine `xtts`, `speaker_wav`, CLI `--speaker-wav`,
      upload nella UI, salvataggio in `uploads/voci-clonate/`.
- [ ] Preset vocali migliori per l'italiano.
- [ ] Implementazione reale dell'adapter Dia.
- [ ] Anteprima voce prima del rendering completo.
- [ ] Profili speaker ottimizzati per poesia.
- [ ] Altre voci Piper e altre lingue nel catalogo (oggi it + en; la UI offre
      anche fr/es/de come lingua di lettura ma senza voci a catalogo).
- [ ] Verificare end-to-end il fix allucinazioni con Ollama e un testo lungo
      reale (annotazioni indicizzate + chunking, commit edb8a8f).

### Pipeline / robustezza
- [ ] Gestione PDF piu robusta.
- [ ] Coda job opzionale per conversioni lunghe.
- [ ] Opzione CLI `--output-dir` (oggi dipende solo dalla config).

### Interfaccia
- [ ] Tradurre anche i messaggi di avanzamento della pipeline (oggi solo in
      italiano: servirebbe passare la lingua della UI dentro il runner).
- [ ] Valutare se il selettore lingua interfaccia debba allineare anche la
      lingua di lettura quando la form e ancora vuota.

### Infrastruttura
- [ ] Valutare container Docker rootless per non creare file di proprieta root.
- [ ] CI: matrice Python (3.12 / 3.13) e pin di ruff/black per evitare derive.
