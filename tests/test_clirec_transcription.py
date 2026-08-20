import sys
import types

from clirec.transcription import CanonicalTranscriptionAdapter


def test_canonical_transcription_adapter_disables_secondary_store(
    monkeypatch, tmp_path
):
    calls = []
    module = types.ModuleType("canonical_stt_for_test")

    def transcribe_file(path, **kwargs):
        calls.append((path, kwargs))
        return {"text": "synthetisch", "backend": "mock", "model": "v1"}

    module.transcribe_file = transcribe_file
    monkeypatch.setitem(sys.modules, module.__name__, module)
    adapter = CanonicalTranscriptionAdapter(module.__name__)
    result = adapter.transcribe(tmp_path / "audio.wav", language="de")
    assert result["text"] == "synthetisch"
    assert calls[0][1]["persist"] is False
