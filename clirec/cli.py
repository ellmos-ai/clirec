"""Command-line interface for clirec."""

from __future__ import annotations

import os
import json
import sys
import textwrap
import threading
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
        _die(
            "usage: clirec validate|list|replay|start|purge-audio|"
            "purge-transcript|recover|episode-export|review-export ..."
        )
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

    if sub == "audio-devices":
        from .audio import get_audio_backend

        for device in get_audio_backend().list_devices():
            print(f"{device['id']}\t{device['label']}")
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

    if sub in {"purge-audio", "purge-transcript"}:
        if len(rest) != 1:
            _die(f"usage: clirec {sub} <file.clirec>")
        from .media import purge_audio, purge_transcript

        changed = (purge_audio if sub == "purge-audio" else purge_transcript)(rest[0])
        print("purged" if changed else "nothing to purge")
        return

    if sub == "transcribe":
        if not rest:
            _die("usage: clirec transcribe <file.clirec> [--module NAME] [--lang de]")
        from .media import attach_transcript
        from .transcription import CanonicalTranscriptionAdapter

        adapter = CanonicalTranscriptionAdapter(
            _option(rest, "--module") or "ellmos_transkription"
        )
        descriptor = attach_transcript(
            rest[0],
            adapter,
            language=_option(rest, "--lang") or "de",
            redacted="--redacted" in rest,
        )
        print(f"transcript attached: {descriptor['path']}")
        return

    if sub == "recover":
        from .media import recover_orphans

        directory = rest[0] if rest else "recordings"
        removed = recover_orphans(directory)
        print(f"recovered: removed {len(removed)} orphan sidecar(s)")
        return

    if sub == "episode-export":
        _episode_export(rest)
        return

    if sub == "review-export":
        _review_export(rest)
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
    audio_enabled = False
    audio_consent = False
    audio_device = None
    audio_partial = False
    global_hotkeys = False
    pause_hotkey = rc.pause_hotkey
    stop_hotkey = rc.stop_hotkey
    names: list[str] = []
    index = 0
    while index < len(rest):
        argument = rest[index]
        if argument == "--allow-unmasked-input":
            allow_unmasked = True
        elif argument == "--audio":
            audio_enabled = True
        elif argument == "--audio-consent":
            audio_consent = True
        elif argument == "--audio-partial-ok":
            audio_partial = True
        elif argument == "--audio-device":
            if index + 1 >= len(rest):
                _die("--audio-device requires a device id")
            index += 1
            audio_device = rest[index]
        elif argument == "--global-hotkeys":
            global_hotkeys = True
        elif argument in {"--pause-hotkey", "--stop-hotkey"}:
            if index + 1 >= len(rest):
                _die(f"{argument} requires a hotkey combination")
            index += 1
            if argument == "--pause-hotkey":
                pause_hotkey = rest[index]
            else:
                stop_hotkey = rest[index]
        elif argument.startswith("-"):
            _die(f"unknown recording option: {argument}")
        else:
            names.append(argument)
        index += 1
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

    audio_backend = None
    if audio_enabled:
        if not audio_consent:
            _die(
                "audio requires --audio-consent after reviewing the privacy warning; "
                "other people and spoken secrets may be captured"
            )
        from .audio import get_audio_backend

        rc.audio_enabled = True
        rc.audio_device = audio_device
        rc.audio_fail_closed = not audio_partial
        audio_backend = get_audio_backend()
        print(
            "AUDIO CONSENT: microphone recording is local, separately purgeable, "
            "and may capture other people or spoken secrets.",
            file=sys.stderr,
        )
    rc.global_hotkeys_enabled = global_hotkeys
    rc.pause_hotkey = pause_hotkey
    rc.stop_hotkey = stop_hotkey

    rec = Recorder(
        backend,
        config=rc,
        probe=probe,
        audio_backend=audio_backend,
        resolution=f"{width}x{height}",
        origin_x=origin_x,
        origin_y=origin_y,
    )
    if sub == "start":
        microphone = f" device={audio_device or 'default'}" if audio_enabled else ""
        print(
            f"RECORDING events={'on'} audio={'on' if audio_enabled else 'off'}"
            f"{microphone} target={rc.recordings_dir}/{name}.clirec - Ctrl+C stops"
        )
        if audio_enabled:
            rec.start(name, audio_consent=True)
        else:
            rec.start(name)
        hotkeys = None
        stop_requested = threading.Event()
        paused = False
        if global_hotkeys:
            from .hotkeys import GlobalHotkeyController

            hotkeys = GlobalHotkeyController(pause_hotkey, stop_hotkey)

            def toggle_pause():
                nonlocal paused
                paused = not paused
                rec.set_paused(paused)
                print("PAUSED" if paused else "RECORDING resumed")

            hotkeys.start(on_pause=toggle_pause, on_stop=stop_requested.set)
            print(f"global hotkeys: pause={pause_hotkey} stop={stop_hotkey}")
        try:
            while not stop_requested.is_set():
                rec.pump()
                time.sleep(0.05)
        except KeyboardInterrupt:
            pass
        finally:
            if hotkeys is not None:
                hotkeys.stop()
        try:
            out = rec.stop()
            path = rec.save(out, name)
            print(
                f"\nSTOPPED saved={path} steps={len(out.steps)} "
                f"audio={'yes' if out.media else 'no'}"
            )
        except Exception as exc:
            _die(f"AUDIO ERROR or save failure: {exc}", 1)
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
              clirec audio-devices
              clirec replay <file.clirec> [--param k=v ...]
              clirec start <name> [--allow-unmasked-input]
                                  [--audio --audio-consent [--audio-device ID]
                                   [--audio-partial-ok]]
                                  [--global-hotkeys [--pause-hotkey COMBO]
                                   [--stop-hotkey COMBO]]
                                      (Ctrl+C to stop & save)
              clirec purge-audio <file.clirec>
              clirec purge-transcript <file.clirec>
              clirec transcribe <file.clirec> [--module NAME] [--lang de] [--redacted]
              clirec recover [recordings-dir]
              clirec episode-export <file.clirec> --out episode.json ...
              clirec review-export <episode.json> --out review.json --kind skill|workflow
            """
        )
    )


def _option(rest: list[str], name: str, *, required: bool = False) -> str | None:
    if name not in rest:
        if required:
            _die(f"missing required option: {name}")
        return None
    index = rest.index(name)
    if index + 1 >= len(rest):
        _die(f"{name} requires a value")
    return rest[index + 1]


def _episode_export(rest: list[str]) -> None:
    if not rest:
        _die("usage: clirec episode-export <file.clirec> --out episode.json ...")
    from .episode import export_episode
    from .format import read

    episode = export_episode(
        read(rest[0]),
        goal=_option(rest, "--goal", required=True) or "",
        expected_outcome=_option(rest, "--expected", required=True) or "",
        actual_outcome=_option(rest, "--actual", required=True) or "",
        outcome_confirmed="--confirmed" in rest,
        export_consent="--consent-export" in rest,
        export_class=_option(rest, "--class") or "local-review",
    )
    output = _option(rest, "--out", required=True) or ""
    with open(output, "x", encoding="utf-8", newline="\n") as handle:
        json.dump(episode, handle, ensure_ascii=False, indent=2)
        handle.write("\n")
    print(f"episode review export: {output}")


def _review_export(rest: list[str]) -> None:
    if not rest:
        _die("usage: clirec review-export <episode.json> --out review.json --kind ...")
    from .episode import build_review_export

    with open(rest[0], "r", encoding="utf-8") as handle:
        episode = json.load(handle)
    review = build_review_export(
        episode,
        kind=_option(rest, "--kind", required=True) or "",
        user_reviewed="--reviewed" in rest,
        existing_target=_option(rest, "--existing-target"),
    )
    output = _option(rest, "--out", required=True) or ""
    with open(output, "x", encoding="utf-8", newline="\n") as handle:
        json.dump(review, handle, ensure_ascii=False, indent=2)
        handle.write("\n")
    print(f"extractor review export: {output} ({review['status']})")


def main() -> None:
    if len(sys.argv) < 2 or sys.argv[1] in ("-h", "--help", "help"):
        _print_help()
        raise SystemExit(0)
    cmd_rec(sys.argv[1:])


if __name__ == "__main__":
    main()
