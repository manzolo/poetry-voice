from __future__ import annotations

from abc import ABC, abstractmethod
from pathlib import Path

from poetry_voice.models import ParsedDocument


class DocumentParser(ABC):
    extensions: set[str]

    @abstractmethod
    def parse(self, path: Path) -> ParsedDocument:
        """Read a document and preserve poetic line structure as much as possible."""
