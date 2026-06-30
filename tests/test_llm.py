import pytest

from poetry_voice.llm.heuristic import HeuristicLLMProvider


@pytest.mark.asyncio
async def test_heuristic_llm_returns_annotation() -> None:
    annotation = await HeuristicLLMProvider().analyze("Sempre caro mi fu\nquest'ermo colle.")
    assert annotation.title == "Sempre caro mi fu"
    assert len(annotation.lines) == 2
    assert annotation.lines[1].pause_after > 1
