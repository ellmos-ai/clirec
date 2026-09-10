# Third-party licences

`clirec` itself is MIT licensed (see [LICENSE](LICENSE)) and the core package has
**no mandatory runtime dependencies**. Every entry below is an *optional* extra:
it is installed only when you ask for it, and it keeps its own licence.

Verified against the Python Package Index on 2026-09-03.

| Extra | Package | Licence | Why it matters |
|---|---|---|---|
| `record` | [`pynput`](https://pypi.org/project/pynput/) | **LGPL-3.0** | The only copyleft dependency in the project. Using it as an unmodified, separately installed library is the ordinary LGPL case; modifying it, or shipping a derived or statically bound build, triggers the relinking and source-availability obligations of the LGPL. |
| `audio` | [`sounddevice`](https://pypi.org/project/sounddevice/) | MIT | Binds the PortAudio library (MIT) and requires `CFFI` (MIT). PortAudio binaries are redistributed by the wheel. |
| `uia` | [`uiautomation`](https://pypi.org/project/uiautomation/) | Apache-2.0 | Windows-only; requires `comtypes` (MIT). Apache-2.0 adds a notice requirement on redistribution. |
| `dev` | `build`, `pytest`, `ruff`, `twine` | MIT / MIT / MIT / Apache-2.0 | Development toolchain only; never part of a runtime install. |

`all` installs `pynput`, `sounddevice` and (on Windows) `uiautomation` together,
and therefore inherits the LGPL-3.0 obligation of `pynput`.

## Practical consequences

- **Plain `pip install` of clirec or any extra**: nothing to do. Each package is
  fetched from PyPI under its own licence and stays separate.
- **Redistributing a bundle, installer, container image or frozen executable**
  that contains these packages: ship the licence texts, and keep `pynput`
  replaceable by the recipient as the LGPL requires.
- **No STT engine is bundled.** `clirec transcribe` imports a module you name
  yourself (`--module` / `CLIREC_STT_MODULE`). Whatever that module and its
  models are licensed under is outside this list and is your responsibility --
  speech models in particular often carry their own, non-MIT terms.

This is a maintenance overview, not legal advice. Check the licence texts that
ship with the installed packages before redistributing anything.
