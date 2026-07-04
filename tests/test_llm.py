from typing import Any

import pytest

from poetry_voice.config.settings import LLMConfig
from poetry_voice.llm.heuristic import HeuristicLLMProvider
from poetry_voice.llm.http_json import (
    HttpJsonLLMProvider,
    chunk_stanzas,
    merge_annotation,
    split_into_stanzas,
)

POEM = "Sempre caro mi fu\nquest'ermo colle.\n\ne questa siepe, che da tanta parte\ndell'ultimo orizzonte il guardo esclude."


@pytest.mark.asyncio
async def test_heuristic_llm_returns_annotation() -> None:
    annotation = await HeuristicLLMProvider().analyze("Sempre caro mi fu\nquest'ermo colle.")
    assert annotation.title == "Sempre caro mi fu"
    assert len(annotation.lines) == 2
    assert annotation.lines[1].pause_after > 1


def test_split_into_stanzas_numbers_lines_continuously() -> None:
    stanzas = split_into_stanzas(POEM)
    assert [[index for index, _ in stanza] for stanza in stanzas] == [[1, 2], [3, 4]]
    assert stanzas[1][0][1] == "e questa siepe, che da tanta parte"


def test_chunk_stanzas_groups_within_limit_and_splits_long_stanza() -> None:
    stanzas = [[(1, "a"), (2, "b")], [(3, "c")], [(4, "d"), (5, "e"), (6, "f"), (7, "g")]]
    chunks = chunk_stanzas(stanzas, max_lines=3)
    flat = [[line for stanza in chunk for line, _ in stanza] for chunk in chunks]
    assert flat == [[1, 2, 3], [4, 5, 6], [7]]


def test_merge_annotation_keeps_original_text_and_degrades_gracefully() -> None:
    source = [(1, "Sempre caro mi fu"), (2, "quest'ermo colle.")]
    items = [
        {"line": 1, "pause_after": 2.0, "emotion": "wonder", "emphasis": ["caro"]},
        {"line": 1, "pause_after": 9.9},  # duplicato: ignorato
        {"line": 2, "volume": 99.0},  # fuori range: ripiego euristico
        {"line": 7, "pause_after": 0.5},  # verso inesistente: ignorato
        "spazzatura",
    ]
    annotation = merge_annotation(source, items, {"title": "L'infinito", "mood": "contemplativo"})
    assert annotation.title == "L'infinito"
    assert [line.text for line in annotation.lines] == [text for _, text in source]
    assert annotation.lines[0].pause_after == 2.0
    assert annotation.lines[0].emotion == "wonder"
    assert annotation.lines[1].pause_after > 1  # euristica: il verso finisce con "."


def test_merge_annotation_missing_lines_fall_back_to_heuristic() -> None:
    source = [(1, "Sempre caro mi fu"), (2, "quest'ermo colle.")]
    annotation = merge_annotation(source, [], {})
    assert len(annotation.lines) == 2
    assert annotation.title == "Sempre caro mi fu"


def test_merge_annotation_invalid_global_fields_use_defaults() -> None:
    source = [(1, "Sempre caro mi fu")]
    annotation = merge_annotation(source, [], {"overall_speed": "warp"})
    assert annotation.overall_speed == "slow"
    assert len(annotation.lines) == 1


def test_ollama_payload_sets_num_ctx() -> None:
    provider = HttpJsonLLMProvider(LLMConfig(num_ctx=4096))
    payload = provider._payload("prompt")
    assert payload["options"]["num_ctx"] == 4096


@pytest.mark.asyncio
async def test_analyze_short_poem_single_request(monkeypatch: pytest.MonkeyPatch) -> None:
    provider = HttpJsonLLMProvider(LLMConfig(max_lines_per_chunk=10))
    prompts: list[str] = []

    async def fake_request(prompt: str) -> dict[str, Any]:
        prompts.append(prompt)
        return {
            "title": "L'infinito",
            "mood": "contemplativo",
            "lines": [
                {"line": index, "pause_after": 0.5, "emotion": "calm"} for index in range(1, 5)
            ],
        }

    monkeypatch.setattr(provider, "_request_json", fake_request)
    annotation = await provider.analyze(POEM)
    assert len(prompts) == 1
    assert "1| Sempre caro mi fu" in prompts[0]
    assert annotation.title == "L'infinito"
    assert [line.text for line in annotation.lines] == [
        "Sempre caro mi fu",
        "quest'ermo colle.",
        "e questa siepe, che da tanta parte",
        "dell'ultimo orizzonte il guardo esclude.",
    ]


@pytest.mark.asyncio
async def test_analyze_long_poem_chunks_and_survives_chunk_failure(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    long_poem = "\n\n".join(
        "\n".join(f"verso {stanza * 4 + line}" for line in range(1, 5)) for stanza in range(2)
    )
    provider = HttpJsonLLMProvider(LLMConfig(max_lines_per_chunk=4))
    calls: list[str] = []

    async def fake_request(prompt: str) -> dict[str, Any]:
        calls.append(prompt)
        if len(calls) == 1:  # overview
            return {"title": "L'infinito", "mood": "contemplativo"}
        if len(calls) == 3:  # secondo blocco: il modello fallisce
            raise ValueError("boom")
        return {
            "lines": [
                {"line": index, "pause_after": 2.0, "emotion": "wonder"} for index in range(1, 5)
            ]
        }

    monkeypatch.setattr(provider, "_request_json", fake_request)
    annotation = await provider.analyze(long_poem)
    assert len(calls) == 3  # overview + 2 blocchi (il secondo fallito, niente retry infiniti)
    assert annotation.title == "L'infinito"
    assert [line.text for line in annotation.lines] == [f"verso {i}" for i in range(1, 9)]
    assert annotation.lines[0].pause_after == 2.0  # dal blocco riuscito
    assert annotation.lines[4].emotion == "contemplative"  # euristica sul blocco fallito


@pytest.mark.asyncio
async def test_analyze_total_failure_falls_back_to_heuristic(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    provider = HttpJsonLLMProvider(LLMConfig())

    async def fake_request(prompt: str) -> dict[str, Any]:
        raise ConnectionError("ollama down")

    monkeypatch.setattr(provider, "_request_json", fake_request)
    annotation = await provider.analyze(POEM)
    assert len(annotation.lines) == 4
    assert annotation.lines[0].text == "Sempre caro mi fu"
