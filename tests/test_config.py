from pathlib import Path

from poetry_voice.config import load_config


def test_load_default_config_when_missing(tmp_path: Path) -> None:
    config = load_config(tmp_path / "missing.yaml")
    assert config.llm.provider == "ollama"
    assert config.tts.engine == "kokoro"
