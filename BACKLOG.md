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

## Da fare / idee

### Accessibilita (priorita alta)
- [ ] Aggiungere una favicon (ora `/favicon.ico` da 404 nei log).
- [ ] Test di accessibilita con screen reader reali (NVDA/VoiceOver).
- [ ] Verificare la barra di avanzamento e il riordino versi con sola tastiera.

### Qualita audio / TTS
- [ ] XTTS v2: risolvere il conflitto di dipendenze coqui-tts/transformers
      (errore `cannot import 'isin_mps_friendly' from transformers.pytorch_utils`,
      serve probabilmente un pin di `transformers`) e verificare la
      sintesi/clonazione reale, preferibilmente su GPU. Wiring gia presente
      (engine `xtts`, `speaker_wav`, CLI `--speaker-wav`, upload nella UI).
- [ ] Preset vocali migliori per l'italiano.
- [ ] Implementazione reale dell'adapter Dia.
- [ ] Stitching audio per verso con inserimento di silenzi naturali.
- [ ] Anteprima voce prima del rendering completo.
- [ ] Profili speaker ottimizzati per poesia.
- [ ] Altre voci Piper e altre lingue nel catalogo.

### Pipeline / robustezza
- [ ] Gestione PDF piu robusta.
- [ ] Coda job opzionale per conversioni lunghe.
- [ ] Opzione CLI `--output-dir` (oggi dipende solo dalla config).

### Infrastruttura
- [ ] Valutare container Docker rootless per non creare file di proprieta root.
- [ ] CI: matrice Python (3.12 / 3.13) e pin di ruff/black per evitare derive.
- [ ] Test per le route della UI (convert, synthesize-annotation, result).
