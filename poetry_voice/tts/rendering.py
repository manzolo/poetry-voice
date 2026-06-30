from __future__ import annotations

from poetry_voice.models import LineAnnotation, PoemAnnotation


def annotation_to_ssml(annotation: PoemAnnotation) -> str:
    parts = ['<speak xml:lang="it-IT">']
    for line in annotation.lines:
        parts.append(_line_to_ssml(line))
    parts.append("</speak>")
    return "\n".join(parts)


def annotation_to_plain_script(annotation: PoemAnnotation) -> str:
    chunks: list[str] = []
    for line in annotation.lines:
        prefix = f"[pausa {line.pause_before:.1f}s] " if line.pause_before else ""
        suffix = f" [pausa {line.pause_after:.1f}s]"
        chunks.append(f"{prefix}{line.text}{suffix}")
    return "\n".join(chunks)


def annotation_to_tts_text(annotation: PoemAnnotation) -> str:
    chunks: list[str] = []
    for line in annotation.lines:
        text = line.text.strip()
        if not text:
            continue
        chunks.append(ensure_soft_punctuation(text))
        if line.breath_after or line.pause_after >= 1.0:
            chunks.append("")
    return "\n".join(chunks).strip()


def ensure_soft_punctuation(text: str) -> str:
    if text.endswith((".", ",", ";", ":", "!", "?", "…")):
        return text
    return f"{text},"


def _line_to_ssml(line: LineAnnotation) -> str:
    text = line.text
    for word in line.emphasis:
        text = text.replace(word, f'<emphasis level="moderate">{word}</emphasis>', 1)
    rate = _rate(line.speed)
    volume = f"{line.volume * 100:.0f}%"
    break_before = f'<break time="{int(line.pause_before * 1000)}ms"/>' if line.pause_before else ""
    break_after = f'<break time="{int(line.pause_after * 1000)}ms"/>'
    return f'{break_before}<prosody rate="{rate}" volume="{volume}">{text}</prosody>{break_after}'


def _rate(speed: str | None) -> str:
    return {
        "very_slow": "x-slow",
        "slow": "slow",
        "medium": "medium",
        "fast": "fast",
        None: "slow",
    }[speed]
