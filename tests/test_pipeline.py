from pathlib import Path

import pytest

from poetry_voice.config.settings import AppConfig
from poetry_voice.pipeline import PoetryVoicePipeline


@pytest.mark.asyncio
async def test_pipeline_generates_audio(tmp_path: Path) -> None:
    poem = tmp_path / "poem.txt"
    poem.write_text("La sera scende\nlenta.", encoding="utf-8")
    config = AppConfig()
    config.pipeline.output_dir = tmp_path / "outputs"
    config.audio.format = "wav"
    result = await PoetryVoicePipeline(config).run(poem)
    assert result.audio_path.exists()
    assert result.annotation.lines
