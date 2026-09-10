"""Adapter contract for canonical, externally maintained STT modules."""

from __future__ import annotations

import importlib
import os
from pathlib import Path
from typing import Protocol, runtime_checkable


#: Environment variable naming the external STT module to import.
STT_MODULE_ENV = "CLIREC_STT_MODULE"

#: Environment variable naming the default transcription language.
STT_LANGUAGE_ENV = "CLIREC_STT_LANGUAGE"

#: Language used when neither ``--lang`` nor ``CLIREC_STT_LANGUAGE`` is set.
DEFAULT_LANGUAGE = "en"


def default_language() -> str:
    """Return the configured default transcription language.

    CLIRec does not guess a language from the host locale, because a silent
    locale-dependent default produces transcripts whose language is not
    reproducible across machines. Set ``CLIREC_STT_LANGUAGE`` or pass
    ``--lang`` explicitly.
    """

    return os.environ.get(STT_LANGUAGE_ENV, "").strip() or DEFAULT_LANGUAGE


def resolve_module_name(explicit: str | None = None) -> str:
    """Return the STT module to import, or raise with the available options.

    There is deliberately no built-in default module. CLIRec implements no STT
    engine and does not ship one, so any hard-coded module name would name a
    package that most installations do not have -- the caller decides.
    """

    name = (explicit or os.environ.get(STT_MODULE_ENV, "")).strip()
    if not name:
        raise RuntimeError(
            "no STT module selected: pass --module NAME or set "
            f"{STT_MODULE_ENV}. The module must expose "
            "transcribe_file(path, language=..., persist=False); see "
            "docs/AUDIO_PRIVACY.md."
        )
    return name


@runtime_checkable
class TranscriptionBackend(Protocol):
    def transcribe(self, audio_path: str | Path, *, language: str = ...) -> dict: ...


class CanonicalTranscriptionAdapter:
    """Import a canonical STT module without creating its default transcript store.

    The module must expose ``transcribe_file(path, language=..., persist=False)``.
    Requiring the explicit ``persist`` switch prevents CLIRec from silently
    producing a second transcript store beside its reviewed transcript sidecar.

    ``module_name`` is required; it comes from ``--module`` or from the
    ``CLIREC_STT_MODULE`` environment variable.
    """

    def __init__(self, module_name: str | None = None):
        self.module_name = resolve_module_name(module_name)

    def transcribe(
        self, audio_path: str | Path, *, language: str | None = None
    ) -> dict:
        language = language or default_language()
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
