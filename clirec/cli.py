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
        return

    if sub in ("start", "stop", "buffer"):
        _rec_live(sub, rest)
        return

    _die(f"unknown clirec subcommand {sub!r}")


def _rec_live(sub: str, rest: list[str]) -> None:
    """Thin live-recording loop. Drives ``Recorder.pump()`` on a timer."""

    from .capture.base import get_backend
    from .config import recorder_config_from_dict
    from .recorder import Recorder
    from .uia_probe import DefaultProbe

    rc = recorder_config_from_dict()
    backend = get_backend()
    rec = Recorder(backend, config=rc, probe=DefaultProbe())
    if sub == "start":
        name = rest[0] if rest else "recording"
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
    print(
        "note: 'stop'/'buffer' require a running daemon session; "
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
              clirec start <name>   (Ctrl+C to stop & save)
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
