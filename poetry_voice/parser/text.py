from __future__ import annotations

from pathlib import Path

from poetry_voice.models import ParsedDocument
from poetry_voice.parser.base import DocumentParser


class TextParser(DocumentParser):
    extensions = {".txt"}

    def parse(self, path: Path) -> ParsedDocument:
        return ParsedDocument(path=path, text=path.read_text(encoding="utf-8"), source_format="txt")
