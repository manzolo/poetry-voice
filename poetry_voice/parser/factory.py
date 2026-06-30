from __future__ import annotations

from pathlib import Path

from poetry_voice.models import ParsedDocument
from poetry_voice.parser.base import DocumentParser
from poetry_voice.parser.markdown import MarkdownParser
from poetry_voice.parser.pdf import PdfParser
from poetry_voice.parser.text import TextParser

PARSERS: tuple[DocumentParser, ...] = (TextParser(), MarkdownParser(), PdfParser())


def parse_document(path: Path | str) -> ParsedDocument:
    document_path = Path(path)
    suffix = document_path.suffix.lower()
    for parser in PARSERS:
        if suffix in parser.extensions:
            return parser.parse(document_path)
    supported = ", ".join(sorted(ext for parser in PARSERS for ext in parser.extensions))
    raise ValueError(f"Formato non supportato: {suffix}. Formati supportati: {supported}")
