from poetry_voice.tts.voices import default_voice_for, validate_voice_for_engine


def test_matching_engine_and_language_is_valid() -> None:
    assert validate_voice_for_engine("piper", "it_IT-paola-medium", "it") is None
    assert validate_voice_for_engine("piper", "en_US-lessac-medium", "en") is None
    assert validate_voice_for_engine("kokoro", "af_heart", "en") is None


def test_wrong_engine_is_rejected() -> None:
    assert validate_voice_for_engine("kokoro", "it_IT-paola-medium") is not None


def test_wrong_language_is_rejected_in_ui_language() -> None:
    message_it = validate_voice_for_engine("piper", "it_IT-paola-medium", "en")
    assert message_it is not None and "lingua" in message_it
    message_en = validate_voice_for_engine("piper", "it_IT-paola-medium", "en", ui_lang="en")
    assert message_en is not None and "language" in message_en


def test_non_catalog_engines_skip_validation() -> None:
    assert validate_voice_for_engine("xtts", "", "en") is None


def test_default_voice_for_engine_and_language() -> None:
    assert default_voice_for("piper", "en").key == "en_US-lessac-medium"
    assert default_voice_for("kokoro", "en").key == "af_heart"
    assert default_voice_for("piper", "it").key == "it_IT-paola-medium"
    assert default_voice_for("piper", "fr") is None
