from __future__ import annotations

from poetry_voice.llm.base import LLMProvider
from poetry_voice.models import LineAnnotation, PoemAnnotation


def heuristic_line(text: str) -> LineAnnotation:
    """Annotazione prosodica di ripiego per un singolo verso, senza LLM."""
    pause_after = 1.1 if text.endswith((".", "!", "?")) else 0.65
    emphasis = [word.strip(".,;:!?") for word in text.split()[:1] if len(word) > 3]
    return LineAnnotation(
        text=text,
        pause_after=pause_after,
        breath_after=pause_after >= 1.0,
        emphasis=emphasis,
        emotion="contemplative",
        speed="slow",
    )


class HeuristicLLMProvider(LLMProvider):
    async def analyze(self, poem: str) -> PoemAnnotation:
        lines = [line.rstrip() for line in poem.splitlines()]
        meaningful = [line for line in lines if line.strip()]
        title = meaningful[0][:80] if meaningful else "Untitled"
        annotations = [heuristic_line(line) for line in lines if line.strip()]
        return PoemAnnotation(title=title, mood="contemplativo", lines=annotations)
