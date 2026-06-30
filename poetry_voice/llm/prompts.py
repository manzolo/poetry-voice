from __future__ import annotations


SYSTEM_PROMPT = """Sei un direttore della lettura poetica.
Analizza una poesia per produrre indicazioni prosodiche utili a una sintesi vocale naturale.
Lo stile deve essere caldo, elegante, rilassante e umano, senza recitazione eccessivamente teatrale.
Rispondi solo con JSON valido, senza markdown."""


def build_analysis_prompt(
    poem: str, language: str, reading_tone: str, speed: str, instructions: str = ""
) -> str:
    instruction_block = (
        f"\nIndicazioni specifiche dell'utente:\n{instructions}\n" if instructions.strip() else ""
    )
    return f"""Annota questa poesia per una lettura espressiva accessibile a persone ipovedenti.

Parametri richiesti dall'utente:
- lingua lettura: {language}
- tono generale desiderato: {reading_tone}
- velocita desiderata: {speed}
{instruction_block}

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
    {{
      "text": "verso originale",
      "pause_before": 0.0,
      "pause_after": 0.8,
      "breath_after": true,
      "emphasis": ["parola"],
      "emotion": "wonder",
      "volume": 1.0,
      "speed": "slow",
      "pitch": 1.0,
      "metadata": {{}}
    }}
  ],
  "metadata": {{}}
}}

Poesia:
{poem}
"""
