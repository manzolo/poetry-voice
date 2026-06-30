from __future__ import annotations

from poetry_voice.llm.base import LLMProvider
from poetry_voice.models import LineAnnotation, PoemAnnotation


class HeuristicLLMProvider(LLMProvider):
    async def analyze(self, poem: str) -> PoemAnnotation:
        lines = [line.rstrip() for line in poem.splitlines()]
        meaningful = [line for line in lines if line.strip()]
        title = meaningful[0][:80] if meaningful else "Untitled"
        annotations: list[LineAnnotation] = []
        for line in lines:
            if not line.strip():
                continue
            pause_after = 1.1 if line.endswith((".", "!", "?")) else 0.65
            emphasis = [word.strip(".,;:!?") for word in line.split()[:1] if len(word) > 3]
            annotations.append(
                LineAnnotation(
                    text=line,
                    pause_after=pause_after,
                    breath_after=pause_after >= 1.0,
                    emphasis=emphasis,
                    emotion="contemplative",
                    speed="slow",
                )
            )
        return PoemAnnotation(title=title, mood="contemplativo", lines=annotations)
