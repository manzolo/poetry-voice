from __future__ import annotations

from pathlib import Path

from markdown_it import MarkdownIt

from poetry_voice.models import ParsedDocument
from poetry_voice.parser.base import DocumentParser


class MarkdownParser(DocumentParser):
    extensions = {".md", ".markdown"}

    def parse(self, path: Path) -> ParsedDocument:
        raw = path.read_text(encoding="utf-8")
        tokens = MarkdownIt().parse(raw)
        lines: list[str] = []
        for token in tokens:
            if token.type in {"inline", "fence", "code_block"} and token.content:
                lines.append(token.content)
            elif token.type == "softbreak":
                lines.append("")
        text = "\n".join(lines).strip() or raw
        return ParsedDocument(path=path, text=text, source_format="markdown")
