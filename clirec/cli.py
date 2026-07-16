"""Command-line interface for clirec."""

from __future__ import annotations

import os
import sys
import textwrap
import time


def _die(message: str, code: int = 2) -> None:
    print(message, file=sys.stderr)
    raise SystemExit(code)


def _parse_params(rest: list[str], start: int = 0) -> dict[str, str]:
    params: dict[str, str] = {}
    i = start
    while i < len(rest):
        if rest[i] == "--param" and i + 1 < len(rest):
            k, sep, v = rest[i + 1].partition("=")
            if not sep:
                _die("usage: clirec replay <file.clirec> [--param k=v ...]")
            params[k] = v
            i += 2
            continue
        i += 1
    return params


def _run_replay(path: str, params: dict[str, str], executor):
    """Load a ``.clirec`` file and replay it against an injected executor."""

    from .format import read
    from .replay import replay

    rec = read(path)
    return replay(rec, executor, params=params or None)


def cmd_rec(args: list[str], *, executor_factory=None) -> None:
    """Run clirec subcommands.

    ``executor_factory`` is optional and used by host integrations such as
    open-compute. Standalone clirec can validate, list, and record without it;
    replay needs a concrete executor because clirec itself stays backend-neutral.
    """

    if not args:
        _die("usage: clirec validate|list|replay|start|stop|buffer ...")
    sub, rest = args[0], args[1:]

    if sub == "validate":
        if not rest:
            _die("usage: clirec validate <file.clirec>")
        if not os.path.exists(rest[0]):
            _die(f"file not found: {rest[0]}")
        from .format import validate

        with open(rest[0], "r", encoding="utf-8") as fh:
            problems = validate(fh.read())
        print("OK" if not problems else "\n".join(problems))
        if problems:
            raise SystemExit(1)
        return

    if sub == "list":
        d = "recordings"
        if "--dir" in rest:
            idx = rest.index("--dir")
            if idx + 1 >= len(rest):
                _die("usage: clirec list [--dir DIR]")
            d = rest[idx + 1]
        if not os.path.isdir(d):
            print(f"(no recordings dir: {d})")
            return
        for fn in sorted(os.listdir(d)):
            if fn.endswith(".clirec"):
                print(fn)
        return

    if sub == "replay":
        if not rest:
            _die("usage: clirec replay <file.clirec> [--param k=v ...]")
        if executor_factory is None:
            _die(
                "clirec replay needs an executor integration. Use `oc rec replay` "
                "from open-compute or pass an executor in Python."
            )
        path = rest[0]
        if not os.path.exists(path):
            _die(f"file not found: {path}")
        rep = _run_replay(path, _parse_params(rest, 1), executor_factory())
        print(
            f"replay: total={rep.total} ok={rep.ok} fallbacks={rep.fallbacks} "
            f"failures={len(rep.failures)}"
        )
        for failure in rep.failures:
            print("  FAIL", failure)
        if rep.failures:
            raise SystemExit(1)
        return

    if sub in ("start", "stop", "buffer"):
        _rec_live(sub, rest)
        return

    _die(f"unknown clirec subcommand {sub!r}")


def _rec_live(sub: str, rest: list[str]) -> None:
    """Thin live-recording loop. Drives ``Recorder.pump()`` on a timer."""

    from .capture.base import get_backend, get_desktop_geometry
    from .config import recorder_config_from_dict
    from .recorder import Recorder, validate_recording_name
    from .uia_probe import DefaultProbe

    rc = recorder_config_from_dict()
    allow_unmasked = False
    names: list[str] = []
    for argument in rest:
        if argument == "--allow-unmasked-input":
            allow_unmasked = True
        elif argument.startswith("-"):
            _die(f"unknown recording option: {argument}")
        else:
            names.append(argument)
    if len(names) > 1:
        _die("clirec start accepts at most one recording name")
    try:
        name = validate_recording_name(names[0] if names else "recording")
    except ValueError as exc:
        _die(str(exc))

    backend = get_backend()
    geometry = get_desktop_geometry()
    if geometry is None:
        _die("desktop geometry is unavailable; refusing to record unusable coordinates")
    origin_x, origin_y, width, height = geometry

    probe = DefaultProbe()
    if allow_unmasked:
        rc.mask_password_fields = False
        print(
            "WARNING: keyboard-input masking is disabled; review the recording before sharing.",
            file=sys.stderr,
        )

    rec = Recorder(
        backend,
        config=rc,
        probe=probe,
        resolution=f"{width}x{height}",
        origin_x=origin_x,
        origin_y=origin_y,
    )
    if sub == "start":
        print(f"recording '{name}' - press Ctrl+C to stop")
        rec.start(name)
        try:
            while True:
                rec.pump()
                time.sleep(0.05)
        except KeyboardInterrupt:
            out = rec.stop()
            path = rec.save(out, name)
            print(f"\nsaved: {path} ({len(out.steps)} steps)")
        return
    _die(
        "'stop'/'buffer' require a running daemon session; "
        "use 'clirec start <name>' (Ctrl+C to stop) for the MVP."
    )


def _print_help() -> None:
    print(
        textwrap.dedent(
            """\
            Usage:
              clirec validate <file.clirec>
              clirec list [--dir DIR]
              clirec replay <file.clirec> [--param k=v ...]
              clirec start <name> [--allow-unmasked-input]
                                      (Ctrl+C to stop & save)
            """
        )
    )


def main() -> None:
    if len(sys.argv) < 2 or sys.argv[1] in ("-h", "--help", "help"):
        _print_help()
        raise SystemExit(0)
    cmd_rec(sys.argv[1:])


if __name__ == "__main__":
    main()
