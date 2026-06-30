from __future__ import annotations

from pathlib import Path

from pypdf import PdfReader

from poetry_voice.models import ParsedDocument
from poetry_voice.parser.base import DocumentParser


class PdfParser(DocumentParser):
    extensions = {".pdf"}

    def parse(self, path: Path) -> ParsedDocument:
        reader = PdfReader(path)
        pages: list[str] = []
        for page in reader.pages:
            text = page.extract_text(extraction_mode="layout") or ""
            pages.append(text.rstrip())
        return ParsedDocument(
            path=path,
            text="\n\n".join(pages).strip(),
            source_format="pdf",
            metadata={"pages": len(reader.pages)},
        )
