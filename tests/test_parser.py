from pathlib import Path

from poetry_voice.parser import parse_document


def test_text_parser_preserves_lines(tmp_path: Path) -> None:
    path = tmp_path / "poem.txt"
    path.write_text("Uno\nDue\n\nTre\n", encoding="utf-8")
    parsed = parse_document(path)
    assert parsed.source_format == "txt"
    assert parsed.text == "Uno\nDue\n\nTre\n"


def test_markdown_parser_extracts_text(tmp_path: Path) -> None:
    path = tmp_path / "poem.md"
    path.write_text("# Titolo\n\nVerso **forte**", encoding="utf-8")
    parsed = parse_document(path)
    assert "Titolo" in parsed.text
    assert "Verso" in parsed.text
