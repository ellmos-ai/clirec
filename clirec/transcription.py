"""Adapter contract for canonical, externally maintained STT modules."""

from __future__ import annotations

import importlib
from pathlib import Path
from typing import Protocol, runtime_checkable


@runtime_checkable
class TranscriptionBackend(Protocol):
    def transcribe(self, audio_path: str | Path, *, language: str = "de") -> dict: ...


class CanonicalTranscriptionAdapter:
    """Import a canonical STT module without creating its default transcript store.

    The module must expose ``transcribe_file(path, language=..., persist=False)``.
    Requiring the explicit ``persist`` switch prevents CLIRec from silently
    producing a second SQLite copy beside its reviewed transcript sidecar.
    """

    def __init__(self, module_name: str = "ellmos_transkription"):
        self.module_name = module_name

    def transcribe(self, audio_path: str | Path, *, language: str = "de") -> dict:
        module = importlib.import_module(self.module_name)
        function = getattr(module, "transcribe_file", None)
        if not callable(function):
            raise RuntimeError(
                f"canonical STT module {self.module_name!r} lacks "
                "transcribe_file(..., persist=False)"
            )
        result = function(str(audio_path), language=language, persist=False)
        if not isinstance(result, dict) or not isinstance(result.get("text"), str):
            raise RuntimeError("canonical STT backend returned an invalid result")
        return result
