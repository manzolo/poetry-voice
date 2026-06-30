from __future__ import annotations

import asyncio
import shutil
from pathlib import Path

from poetry_voice.config.settings import AudioConfig


async def post_process_audio(input_wav: Path, output_path: Path, config: AudioConfig) -> Path:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    if shutil.which("ffmpeg") is None and output_path.suffix.lower() == ".wav":
        shutil.copyfile(input_wav, output_path)
        return output_path

    filters = [f"loudnorm=I={config.lufs}:TP=-1.5:LRA=11"]
    if config.light_compression:
        filters.append("acompressor=threshold=-18dB:ratio=2:attack=20:release=250")
    if config.fade_ms > 0:
        fade_seconds = config.fade_ms / 1000
        filters.append(f"afade=t=in:st=0:d={fade_seconds}")

    command = [
        "ffmpeg",
        "-y",
        "-i",
        str(input_wav),
        "-af",
        ",".join(filters),
    ]
    if output_path.suffix.lower() in {".mp3", ".ogg"}:
        command.extend(["-b:a", config.bitrate])
    command.append(str(output_path))

    process = await asyncio.create_subprocess_exec(
        *command,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE,
    )
    _, stderr = await process.communicate()
    if process.returncode != 0:
        raise RuntimeError(f"FFmpeg non riuscito: {stderr.decode('utf-8', errors='ignore')}")
    return output_path
