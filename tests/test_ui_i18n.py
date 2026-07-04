from fastapi.testclient import TestClient

from poetry_voice.ui.app import app
from poetry_voice.ui.i18n import _STRINGS, UI_LANGUAGES, translations


def test_every_string_exists_in_every_ui_language() -> None:
    for key, values in _STRINGS.items():
        assert set(values) == set(UI_LANGUAGES), f"traduzioni incomplete per '{key}'"


def test_unknown_ui_language_falls_back_to_italian() -> None:
    assert translations("xx") == translations("it")


def test_index_defaults_to_italian() -> None:
    client = TestClient(app)
    response = client.get("/")
    assert response.status_code == 200
    assert 'lang="it"' in response.text
    assert "Genera audiolibro" in response.text


def test_index_in_english_sets_cookie_and_persists() -> None:
    client = TestClient(app)
    response = client.get("/?lang=en")
    assert 'lang="en"' in response.text
    assert "Generate audiobook" in response.text
    assert response.cookies.get("poetryvoice_ui_lang") == "en"
    # Alla visita successiva la lingua resta inglese grazie al cookie.
    response = client.get("/")
    assert "Generate audiobook" in response.text


def test_voices_carry_language_for_client_side_filtering() -> None:
    client = TestClient(app)
    response = client.get("/")
    assert 'data-language="en"' in response.text
    assert 'data-language="it"' in response.text


def test_index_has_new_controls() -> None:
    client = TestClient(app)
    text = client.get("/").text
    assert 'name="source_mode"' in text  # switch upload/testo
    assert 'id="stop-button"' in text
    assert 'id="ollama-models"' in text  # datalist modelli
    assert 'id="layout-toggle"' in text


def test_cancel_unknown_job_returns_404() -> None:
    client = TestClient(app)
    response = client.post("/jobs/nonexistent/cancel")
    assert response.status_code == 404


def test_ollama_models_endpoint_degrades_to_empty_list() -> None:
    client = TestClient(app)
    response = client.get("/ollama-models")
    assert response.status_code == 200
    assert isinstance(response.json()["models"], list)


def test_job_can_be_cancelled(tmp_path, monkeypatch) -> None:  # noqa: ANN001
    import poetry_voice.ui.app as app_module

    monkeypatch.setattr(app_module, "UPLOAD_DIR", tmp_path)
    client = TestClient(app)
    response = client.post(
        "/convert",
        data={
            "tts_engine": "piper",
            "tts_speaker": "it_IT-paola-medium",
            "language": "it",
            "source_text": "Sempre caro mi fu\nquest'ermo colle.",
        },
    )
    assert response.status_code == 200
    job_id = response.json()["job_id"]
    cancel = client.post(f"/jobs/{job_id}/cancel")
    assert cancel.status_code == 200
    for _ in range(50):
        status = client.get(f"/jobs/{job_id}").json()["status"]
        if status in {"cancelled", "completed", "failed"}:
            break
    assert status in {"cancelled", "completed", "failed"}


def test_convert_rejects_voice_language_mismatch() -> None:
    client = TestClient(app)
    response = client.post(
        "/convert",
        data={
            "tts_engine": "piper",
            "tts_speaker": "it_IT-paola-medium",
            "language": "en",
            "source_text": "A poem",
        },
    )
    assert response.status_code == 400
    assert "lingua" in response.json()["error"]
