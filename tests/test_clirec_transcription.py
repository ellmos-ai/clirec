import pathlib
import re
import sys
import types

import pytest

from clirec.transcription import (
    DEFAULT_LANGUAGE,
    STT_LANGUAGE_ENV,
    STT_MODULE_ENV,
    CanonicalTranscriptionAdapter,
    default_language,
    resolve_module_name,
)


def test_canonical_transcription_adapter_disables_secondary_store(
    monkeypatch, tmp_path
):
    calls = []
    module = types.ModuleType("canonical_stt_for_test")

    def transcribe_file(path, **kwargs):
        calls.append((path, kwargs))
        return {"text": "synthetic", "backend": "mock", "model": "v1"}

    module.transcribe_file = transcribe_file
    monkeypatch.setitem(sys.modules, module.__name__, module)
    adapter = CanonicalTranscriptionAdapter(module.__name__)
    result = adapter.transcribe(tmp_path / "audio.wav", language="de")
    assert result["text"] == "synthetic"
    assert calls[0][1]["persist"] is False
    assert calls[0][1]["language"] == "de"


def test_module_must_be_selected_explicitly(monkeypatch):
    monkeypatch.delenv(STT_MODULE_ENV, raising=False)
    with pytest.raises(RuntimeError) as error:
        resolve_module_name(None)
    # The error has to name both ways out, otherwise the user is stuck.
    assert "--module" in str(error.value)
    assert STT_MODULE_ENV in str(error.value)


def test_module_can_come_from_environment(monkeypatch):
    monkeypatch.setenv(STT_MODULE_ENV, "some_stt_module")
    assert resolve_module_name(None) == "some_stt_module"
    assert resolve_module_name("explicit_wins") == "explicit_wins"


def test_language_default_is_neutral_and_overridable(monkeypatch):
    monkeypatch.delenv(STT_LANGUAGE_ENV, raising=False)
    assert default_language() == DEFAULT_LANGUAGE == "en"
    monkeypatch.setenv(STT_LANGUAGE_ENV, "de")
    assert default_language() == "de"


def test_no_organisation_specific_stt_module_is_hardcoded():
    """No private or organisation-internal module name may be a built-in default.

    Until 2026-09-03 the adapter defaulted to a module that is published
    nowhere: every public user hit ``ModuleNotFoundError`` on the only
    documented STT path, and the private naming leaked into the source. A
    default that names a package the installation cannot have is a dead end,
    not a convenience -- so there is no built-in default at all.
    """

    root = pathlib.Path(__file__).resolve().parents[1] / "clirec"
    forbidden = re.compile(r"ellmos[_-]|_control-center|OneDrive", re.IGNORECASE)
    offenders = [
        f"{path.name}:{number}: {line.strip()}"
        for path in sorted(root.rglob("*.py"))
        for number, line in enumerate(
            path.read_text(encoding="utf-8").splitlines(), start=1
        )
        if forbidden.search(line)
    ]
    assert not offenders, "organisation-internal names in shipped code: " + "; ".join(
        offenders
    )
