from poetry_voice.config.settings import PipelineConfig
from poetry_voice.pipeline.segmentation import split_into_sentences


def test_splits_on_sentence_punctuation() -> None:
    text = "Prima frase. Seconda frase! E la terza? Poi i puntini… E fine."
    assert split_into_sentences(text).splitlines() == [
        "Prima frase.",
        "Seconda frase!",
        "E la terza?",
        "Poi i puntini…",
        "E fine.",
    ]


def test_joins_line_breaks_inside_paragraphs() -> None:
    text = "Una frase spezzata\nsu piu righe dal PDF. Poi un'altra\nfrase."
    assert split_into_sentences(text).splitlines() == [
        "Una frase spezzata su piu righe dal PDF.",
        "Poi un'altra frase.",
    ]


def test_preserves_paragraph_breaks_as_stanza_separators() -> None:
    text = "Primo paragrafo. Con due frasi.\n\nSecondo paragrafo."
    assert split_into_sentences(text) == ("Primo paragrafo.\nCon due frasi.\n\nSecondo paragrafo.")


def test_does_not_split_on_commas_or_semicolons() -> None:
    text = "Una frase lunga, con virgole; e punti e virgola: resta intera."
    assert split_into_sentences(text) == text


def test_default_segmentation_is_lines() -> None:
    assert PipelineConfig().segmentation == "lines"
