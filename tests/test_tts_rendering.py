from poetry_voice.models import LineAnnotation, PoemAnnotation
from poetry_voice.tts.rendering import annotation_to_ssml, annotation_to_tts_text


def test_annotation_to_ssml_includes_breaks_and_emphasis() -> None:
    annotation = PoemAnnotation(
        title="Test",
        lines=[
            LineAnnotation(
                text="Sempre caro",
                pause_after=0.8,
                emphasis=["Sempre"],
                speed="slow",
            )
        ],
    )
    ssml = annotation_to_ssml(annotation)
    assert "<speak" in ssml
    assert "emphasis" in ssml
    assert 'break time="800ms"' in ssml


def test_annotation_to_tts_text_does_not_speak_pause_markers() -> None:
    annotation = PoemAnnotation(
        title="Test",
        lines=[LineAnnotation(text="Sempre caro", pause_after=0.8, speed="slow")],
    )
    text = annotation_to_tts_text(annotation)
    assert "pausa" not in text
    assert "Sempre caro" in text
