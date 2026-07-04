from __future__ import annotations

SYSTEM_PROMPT = """Sei un direttore della lettura poetica.
Analizza una poesia per produrre indicazioni prosodiche utili a una sintesi vocale naturale.
Lo stile deve essere caldo, elegante, rilassante e umano, senza recitazione eccessivamente teatrale.
Rispondi solo con JSON valido, senza markdown."""

# Il testo dei versi NON viene mai rigenerato dall'LLM: i versi arrivano
# numerati ("numero| testo") e le annotazioni tornano indicizzate per numero.
# Il testo letto dal TTS resta per costruzione quello del file originale.

_LINE_ITEM_SCHEMA = """{
      "line": 1,
      "pause_before": 0.0,
      "pause_after": 0.8,
      "breath_after": true,
      "emphasis": ["parola"],
      "emotion": "wonder",
      "volume": 1.0,
      "speed": "slow",
      "pitch": 1.0
    }"""


def format_numbered_stanzas(stanzas: list[list[tuple[int, str]]]) -> str:
    blocks = []
    for stanza in stanzas:
        blocks.append("\n".join(f"{index}| {text}" for index, text in stanza))
    return "\n\n".join(blocks)


def _user_parameters(language: str, reading_tone: str, speed: str, instructions: str) -> str:
    instruction_block = (
        f"\nIndicazioni specifiche dell'utente:\n{instructions}\n" if instructions.strip() else ""
    )
    return f"""Parametri richiesti dall'utente:
- lingua lettura: {language}
- tono generale desiderato: {reading_tone}
- velocita desiderata: {speed}
{instruction_block}"""


def _line_rules(first_line: int, last_line: int) -> str:
    return f"""Regole importanti:
- Ogni verso e preceduto dal suo numero nel formato "numero| testo".
- In "line" riporta quel numero; NON riscrivere il testo del verso.
- Fornisci una voce in "lines" per ogni verso da {first_line} a {last_line}, in ordine,
  senza salti ne ripetizioni."""


def build_analysis_prompt(
    numbered_poem: str,
    language: str,
    reading_tone: str,
    speed: str,
    instructions: str = "",
    first_line: int = 1,
    last_line: int = 1,
) -> str:
    return f"""Annota questa poesia per una lettura espressiva accessibile a persone ipovedenti.

{_user_parameters(language, reading_tone, speed, instructions)}
Individua:
- emozione dominante;
- emozione di ogni verso;
- pause prima/dopo ogni verso;
- respirazioni naturali;
- parole da enfatizzare;
- ritmo, velocita, volume relativo e intonazione.

Schema JSON richiesto:
{{
  "title": "titolo se deducibile",
  "author": null,
  "language": "{language}",
  "mood": "nostalgico|sereno|malinconico|solenne|...",
  "overall_speed": "very_slow|slow|medium|fast",
  "voice_style": "warm|neutral|bright|deep|soft",
  "lines": [
    {_LINE_ITEM_SCHEMA}
  ],
  "metadata": {{}}
}}

{_line_rules(first_line, last_line)}

Poesia:
{numbered_poem}
"""


def build_overview_prompt(
    numbered_poem: str,
    language: str,
    reading_tone: str,
    speed: str,
    instructions: str = "",
) -> str:
    return f"""Leggi questa poesia e descrivine solo le caratteristiche globali
per una lettura espressiva accessibile a persone ipovedenti.

{_user_parameters(language, reading_tone, speed, instructions)}
Schema JSON richiesto:
{{
  "title": "titolo se deducibile",
  "author": null,
  "language": "{language}",
  "mood": "nostalgico|sereno|malinconico|solenne|...",
  "overall_speed": "very_slow|slow|medium|fast",
  "voice_style": "warm|neutral|bright|deep|soft"
}}

Non includere il testo della poesia nella risposta.

Poesia:
{numbered_poem}
"""


def build_chunk_prompt(
    numbered_chunk: str,
    title: str,
    mood: str,
    first_line: int,
    last_line: int,
    total_lines: int,
    language: str,
    reading_tone: str,
    speed: str,
    instructions: str = "",
) -> str:
    poem_ref = f'della poesia "{title}"' if title else "di una poesia"
    return f"""Annota i versi da {first_line} a {last_line} (su {total_lines} totali) {poem_ref}
per una lettura espressiva accessibile a persone ipovedenti.
Emozione dominante della poesia: {mood}.

{_user_parameters(language, reading_tone, speed, instructions)}
Individua per ogni verso: pause prima/dopo, respirazioni naturali,
parole da enfatizzare, emozione, volume relativo, velocita e intonazione.

Schema JSON richiesto:
{{
  "lines": [
    {_LINE_ITEM_SCHEMA}
  ]
}}

{_line_rules(first_line, last_line)}

Versi:
{numbered_chunk}
"""
