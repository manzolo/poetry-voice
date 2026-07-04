from __future__ import annotations

from fastapi import Request

# Lingue dell'interfaccia (indipendenti dalla lingua di lettura della poesia).
UI_LANGUAGES = ("it", "en")
DEFAULT_UI_LANGUAGE = "it"
LANG_COOKIE = "poetryvoice_ui_lang"

# Ogni chiave deve esistere per tutte le lingue: il test di parita' lo verifica.
_STRINGS: dict[str, dict[str, str]] = {
    "app_subtitle": {
        "it": "Lettura espressiva di poesie",
        "en": "Expressive poetry reading",
    },
    "switcher_label": {"it": "Lingua dell'interfaccia", "en": "Interface language"},
    "layout_compact": {"it": "Layout compatto", "en": "Compact layout"},
    "form_aria": {"it": "Converti poesia", "en": "Convert poem"},
    "label_source": {"it": "Sorgente del testo", "en": "Text source"},
    "source_file": {"it": "Carica un file", "en": "Upload a file"},
    "source_write": {"it": "Scrivi o incolla il testo", "en": "Write or paste the text"},
    "label_file": {
        "it": "File poesia TXT, Markdown o PDF",
        "en": "Poem file: TXT, Markdown or PDF",
    },
    "label_text": {"it": "Testo della poesia", "en": "Poem text"},
    "label_engine": {"it": "Motore TTS", "en": "TTS engine"},
    "label_voice": {"it": "Voce", "en": "Voice"},
    "no_voice_option": {
        "it": "Nessuna voce compatibile registrata",
        "en": "No compatible voice registered",
    },
    "label_clone": {
        "it": "Campione voce per clonazione (XTTS) - audio WAV, MP3, FLAC o OGG",
        "en": "Voice sample for cloning (XTTS) - WAV, MP3, FLAC or OGG audio",
    },
    "clone_hint": {
        "it": "Carica 6-15 secondi di voce pulita: XTTS la clona per leggere la poesia.",
        "en": "Upload 6-15 seconds of clean speech: XTTS clones it to read the poem.",
    },
    "label_language": {"it": "Lingua di lettura", "en": "Reading language"},
    "language_hint": {
        "it": "È la lingua della poesia e determina le voci disponibili. "
        "La lingua dell'interfaccia si cambia in alto a destra.",
        "en": "This is the poem's language and determines the available voices. "
        "The interface language is switched at the top right.",
    },
    "lang_it": {"it": "Italiano", "en": "Italian"},
    "lang_en": {"it": "Inglese", "en": "English"},
    "lang_fr": {"it": "Francese", "en": "French"},
    "lang_es": {"it": "Spagnolo", "en": "Spanish"},
    "lang_de": {"it": "Tedesco", "en": "German"},
    "label_split": {"it": "Suddivisione del testo", "en": "Text splitting"},
    "split_lines": {"it": "Per versi (a capo)", "en": "By line breaks (verses)"},
    "split_sentences": {
        "it": "Per frasi (punteggiatura)",
        "en": "By sentences (punctuation)",
    },
    "split_hint": {
        "it": "Per le poesie usa i versi; per la prosa conviene la punteggiatura.",
        "en": "Use verses for poems; punctuation works better for prose.",
    },
    "label_tone": {"it": "Tono", "en": "Tone"},
    "tone_caldo": {"it": "Caldo", "en": "Warm"},
    "tone_neutro": {"it": "Neutro", "en": "Neutral"},
    "tone_sereno": {"it": "Sereno", "en": "Serene"},
    "tone_malinconico": {"it": "Malinconico", "en": "Melancholic"},
    "tone_solenne": {"it": "Solenne", "en": "Solemn"},
    "tone_delicato": {"it": "Delicato", "en": "Gentle"},
    "label_speed": {"it": "Velocità", "en": "Speed"},
    "speed_slow": {"it": "Lenta", "en": "Slow"},
    "speed_very_slow": {"it": "Molto lenta", "en": "Very slow"},
    "speed_medium": {"it": "Media", "en": "Medium"},
    "speed_fast": {"it": "Veloce", "en": "Fast"},
    "label_llm_provider": {"it": "Provider LLM", "en": "LLM provider"},
    "llm_openai": {"it": "OpenAI compatibile", "en": "OpenAI compatible"},
    "llm_generic": {"it": "API generica", "en": "Generic API"},
    "label_llm_model": {"it": "Modello LLM", "en": "LLM model"},
    "model_hint": {
        "it": "Scrivi un nome oppure scegli un modello già scaricato in Ollama.",
        "en": "Type a name or pick a model already downloaded in Ollama.",
    },
    "submit": {"it": "Genera audiolibro", "en": "Generate audiobook"},
    "stop": {"it": "Ferma elaborazione", "en": "Stop processing"},
    "status_starting": {"it": "Avvio elaborazione...", "en": "Starting processing..."},
    "progress_aria": {"it": "Avanzamento elaborazione", "en": "Processing progress"},
    "meta_tone": {"it": "Tono", "en": "Tone"},
    "meta_voice_style": {"it": "Stile voce", "en": "Voice style"},
    "audio_aria": {"it": "Anteprima audio generato", "en": "Generated audio preview"},
    "download": {"it": "Download audio", "en": "Download audio"},
    "preview_title": {"it": "Anteprima annotata", "en": "Annotated preview"},
    "line_label": {"it": "Verso", "en": "Line"},
    "label_pause": {"it": "Pausa dopo", "en": "Pause after"},
    "label_emotion": {"it": "Emozione", "en": "Emotion"},
    "emotion_contemplative": {"it": "Contemplativa", "en": "Contemplative"},
    "emotion_calm": {"it": "Calma", "en": "Calm"},
    "emotion_melancholic": {"it": "Malinconica", "en": "Melancholic"},
    "emotion_tender": {"it": "Tenera", "en": "Tender"},
    "emotion_solemn": {"it": "Solenne", "en": "Solemn"},
    "emotion_wonder": {"it": "Meraviglia", "en": "Wonder"},
    "emotion_tense": {"it": "Tesa", "en": "Tense"},
    "actions_group": {"it": "Azioni verso", "en": "Line actions"},
    "actions": {"it": "Azioni", "en": "Actions"},
    "move_up": {"it": "Sposta il verso su", "en": "Move line up"},
    "move_up_short": {"it": "Sposta su", "en": "Move up"},
    "move_down": {"it": "Sposta il verso giù", "en": "Move line down"},
    "move_down_short": {"it": "Sposta giù", "en": "Move down"},
    "add_line": {"it": "Aggiungi un verso sotto", "en": "Add a line below"},
    "add_line_short": {"it": "Aggiungi verso sotto", "en": "Add line below"},
    "delete_line": {"it": "Elimina il verso", "en": "Delete line"},
    "delete_line_short": {"it": "Elimina verso", "en": "Delete line"},
    "meta_volume": {"it": "Volume", "en": "Volume"},
    "meta_speed": {"it": "velocità", "en": "speed"},
    "resynthesize": {
        "it": "Rigenera da anteprima modificata",
        "en": "Regenerate from edited preview",
    },
    # Stringhe usate dal JavaScript della pagina.
    "js_processing": {"it": "Elaborazione...", "en": "Processing..."},
    "js_started": {"it": "Elaborazione avviata", "en": "Processing started"},
    "js_no_voice": {
        "it": "Nessuna voce compatibile per motore e lingua selezionati.",
        "en": "No compatible voice for the selected engine and language.",
    },
    "js_xtts_sample": {
        "it": "Per XTTS carica un campione voce da clonare.",
        "en": "For XTTS, upload a voice sample to clone.",
    },
    "js_start_failed": {
        "it": "Avvio conversione non riuscito",
        "en": "Failed to start the conversion",
    },
    "js_completed": {"it": "Elaborazione completata", "en": "Processing completed"},
    "js_failed": {"it": "Elaborazione non riuscita", "en": "Processing failed"},
    "js_no_text": {
        "it": "Scrivi o incolla il testo della poesia.",
        "en": "Write or paste the poem text.",
    },
    "js_stopping": {"it": "Interruzione in corso...", "en": "Stopping..."},
    "js_cancelled": {"it": "Elaborazione annullata", "en": "Processing cancelled"},
    "js_in_progress": {"it": "Elaborazione in corso", "en": "Processing"},
    "js_resynthesizing": {
        "it": "Rigenerazione da anteprima modificata",
        "en": "Regenerating from edited preview",
    },
    "js_resynthesize_failed": {
        "it": "Rigenerazione non riuscita",
        "en": "Regeneration failed",
    },
    # Messaggi d'errore lato server.
    "error_no_input": {
        "it": "Carica un file oppure usa il testo estratto modificabile.",
        "en": "Upload a file or use the editable extracted text.",
    },
    "error_invalid_annotation": {
        "it": "Annotazione non valida",
        "en": "Invalid annotation",
    },
    "error_result_missing": {
        "it": "Risultato non disponibile o job non completato.",
        "en": "Result not available or job not completed.",
    },
    "error_job_not_found": {"it": "Job non trovato", "en": "Job not found"},
}


def translations(lang: str) -> dict[str, str]:
    lang = lang if lang in UI_LANGUAGES else DEFAULT_UI_LANGUAGE
    return {key: values[lang] for key, values in _STRINGS.items()}


def resolve_ui_lang(request: Request) -> str:
    """Lingua dell'interfaccia: query string (?lang=), poi cookie, poi default."""
    candidate = request.query_params.get("lang") or request.cookies.get(LANG_COOKIE)
    return candidate if candidate in UI_LANGUAGES else DEFAULT_UI_LANGUAGE
