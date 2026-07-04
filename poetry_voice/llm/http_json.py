from __future__ import annotations

import json
from typing import Any

import httpx
import structlog
from pydantic import ValidationError

from poetry_voice.config.settings import LLMConfig
from poetry_voice.llm.base import LLMProvider
from poetry_voice.llm.heuristic import HeuristicLLMProvider, heuristic_line
from poetry_voice.llm.prompts import (
    SYSTEM_PROMPT,
    build_analysis_prompt,
    build_chunk_prompt,
    build_overview_prompt,
    format_numbered_stanzas,
)
from poetry_voice.models import LineAnnotation, PoemAnnotation

logger = structlog.get_logger(__name__)

NumberedLine = tuple[int, str]
Stanza = list[NumberedLine]

_LINE_FIELDS = frozenset(
    {
        "pause_before",
        "pause_after",
        "breath_after",
        "emphasis",
        "emotion",
        "volume",
        "speed",
        "pitch",
        "metadata",
    }
)
_GLOBAL_FIELDS = ("title", "author", "language", "mood", "overall_speed", "voice_style")


class HttpJsonLLMProvider(LLMProvider):
    def __init__(self, config: LLMConfig) -> None:
        self.config = config
        self.fallback = HeuristicLLMProvider()

    async def analyze(self, poem: str) -> PoemAnnotation:
        stanzas = split_into_stanzas(poem)
        source_lines = [line for stanza in stanzas for line in stanza]
        if not source_lines:
            return await self.fallback.analyze(poem)
        try:
            chunks = chunk_stanzas(stanzas, self.config.max_lines_per_chunk)
            if len(chunks) == 1:
                globals_data = await self._request_json(
                    build_analysis_prompt(
                        format_numbered_stanzas(stanzas),
                        language=self.config.language,
                        reading_tone=self.config.reading_tone,
                        speed=self.config.reading_speed,
                        instructions=self.config.reading_instructions,
                        first_line=source_lines[0][0],
                        last_line=source_lines[-1][0],
                    )
                )
                items = _line_items(globals_data)
            else:
                globals_data, items = await self._analyze_chunked(stanzas, chunks)
        except Exception as exc:
            logger.warning("llm_analysis_failed_using_heuristic", error=str(exc))
            return await self.fallback.analyze(poem)
        return merge_annotation(source_lines, items, globals_data)

    async def _analyze_chunked(
        self, stanzas: list[Stanza], chunks: list[list[Stanza]]
    ) -> tuple[dict[str, Any], list[Any]]:
        # Prima una passata leggera per titolo/tono globale (output minuscolo,
        # niente rischio di loop), poi ogni blocco di strofe con quel contesto.
        total_lines = sum(len(stanza) for stanza in stanzas)
        overview = await self._request_json(
            build_overview_prompt(
                format_numbered_stanzas(stanzas),
                language=self.config.language,
                reading_tone=self.config.reading_tone,
                speed=self.config.reading_speed,
                instructions=self.config.reading_instructions,
            )
        )
        title = overview.get("title")
        mood = overview.get("mood")
        items: list[Any] = []
        for chunk in chunks:
            chunk_lines = [line for stanza in chunk for line in stanza]
            first_line, last_line = chunk_lines[0][0], chunk_lines[-1][0]
            try:
                data = await self._request_json(
                    build_chunk_prompt(
                        format_numbered_stanzas(chunk),
                        title=title if isinstance(title, str) else "",
                        mood=mood if isinstance(mood, str) else self.config.reading_tone,
                        first_line=first_line,
                        last_line=last_line,
                        total_lines=total_lines,
                        language=self.config.language,
                        reading_tone=self.config.reading_tone,
                        speed=self.config.reading_speed,
                        instructions=self.config.reading_instructions,
                    )
                )
                items.extend(_line_items(data))
            except Exception as exc:
                logger.warning(
                    "llm_chunk_failed_using_heuristic_lines",
                    first_line=first_line,
                    last_line=last_line,
                    error=str(exc),
                )
        return overview, items

    async def _request_json(self, prompt: str) -> dict[str, Any]:
        payload = self._payload(prompt)
        headers = {"Content-Type": "application/json"}
        if self.config.api_key:
            headers["Authorization"] = f"Bearer {self.config.api_key}"
        async with httpx.AsyncClient(timeout=self.config.timeout_seconds) as client:
            response = await client.post(self._endpoint(), json=payload, headers=headers)
            response.raise_for_status()
        data = json.loads(self._extract_content(response.json()))
        if not isinstance(data, dict):
            raise ValueError("LLM response is not a JSON object")
        return data

    def _endpoint(self) -> str:
        base = self.config.base_url.rstrip("/")
        if self.config.provider == "ollama":
            return f"{base}/api/chat"
        return f"{base}/v1/chat/completions"

    def _payload(self, prompt: str) -> dict[str, Any]:
        messages = [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": prompt},
        ]
        if self.config.provider == "ollama":
            return {
                "model": self.config.model,
                "messages": messages,
                "stream": False,
                "format": "json",
                "options": {
                    "temperature": self.config.temperature,
                    # I default del server (2048-4096 token) troncano i testi
                    # lunghi in silenzio e mandano il modello in loop.
                    "num_ctx": self.config.num_ctx,
                },
            }
        return {
            "model": self.config.model,
            "messages": messages,
            "temperature": self.config.temperature,
            "response_format": {"type": "json_object"},
        }

    def _extract_content(self, data: dict[str, Any]) -> str:
        if self.config.provider == "ollama":
            return data["message"]["content"]
        return data["choices"][0]["message"]["content"]


def split_into_stanzas(poem: str) -> list[Stanza]:
    """Divide il testo in strofe di versi numerati (1-based, righe vuote escluse)."""
    stanzas: list[Stanza] = []
    current: Stanza = []
    index = 0
    for raw in poem.splitlines():
        if not raw.strip():
            if current:
                stanzas.append(current)
                current = []
            continue
        index += 1
        current.append((index, raw.rstrip()))
    if current:
        stanzas.append(current)
    return stanzas


def chunk_stanzas(stanzas: list[Stanza], max_lines: int) -> list[list[Stanza]]:
    """Raggruppa strofe consecutive in blocchi di al piu' max_lines versi.

    Una strofa piu' lunga di max_lines viene spezzata: meglio un taglio
    interno che un blocco fuori misura.
    """
    chunks: list[list[Stanza]] = []
    current: list[Stanza] = []
    count = 0
    for stanza in stanzas:
        parts = [stanza[i : i + max_lines] for i in range(0, len(stanza), max_lines)]
        for part in parts:
            if current and count + len(part) > max_lines:
                chunks.append(current)
                current, count = [], 0
            current.append(part)
            count += len(part)
    if current:
        chunks.append(current)
    return chunks


def merge_annotation(
    source_lines: list[NumberedLine],
    items: list[Any],
    globals_data: dict[str, Any],
) -> PoemAnnotation:
    """Riattacca le annotazioni indicizzate ai versi originali.

    Il testo letto dal TTS viene sempre dal file parsato: un LLM che ripete o
    inventa versi puo' al massimo degradare le pause, mai il testo. I versi
    senza annotazione valida ricadono sull'euristica, con log esplicito.
    """
    by_index: dict[int, dict[str, Any]] = {}
    for item in items:
        if not isinstance(item, dict):
            continue
        index = item.get("line")
        if isinstance(index, bool) or not isinstance(index, int) or index in by_index:
            continue
        by_index[index] = item
    lines: list[LineAnnotation] = []
    degraded: list[int] = []
    for index, text in source_lines:
        item = by_index.pop(index, None)
        annotation = _line_annotation(text, item) if item is not None else None
        if annotation is None:
            degraded.append(index)
            annotation = heuristic_line(text)
        lines.append(annotation)
    if degraded:
        logger.warning("llm_lines_missing_or_invalid_using_heuristic", lines=degraded)
    if by_index:
        logger.warning("llm_unknown_line_indices_ignored", lines=sorted(by_index))
    fields = {key: globals_data[key] for key in _GLOBAL_FIELDS if globals_data.get(key) is not None}
    fields.setdefault("title", source_lines[0][1][:80])
    try:
        return PoemAnnotation.model_validate({**fields, "lines": lines})
    except ValidationError:
        logger.warning("llm_global_fields_invalid_using_defaults", fields=sorted(fields))
        return PoemAnnotation(lines=lines)


def _line_annotation(text: str, item: dict[str, Any]) -> LineAnnotation | None:
    payload = {key: value for key, value in item.items() if key in _LINE_FIELDS}
    payload["text"] = text
    try:
        return LineAnnotation.model_validate(payload)
    except ValidationError:
        return None


def _line_items(data: dict[str, Any]) -> list[Any]:
    items = data.get("lines")
    return items if isinstance(items, list) else []
