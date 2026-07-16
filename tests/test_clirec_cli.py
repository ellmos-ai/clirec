"""Tests for the clirec CLI."""
import os
import pytest

from clirec import cli
from clirec.format import Recording, Step, write


def _mk(tmp_path):
    rec = Recording("t", "now", "H", "1000x500", steps=[
        Step(1, 0.0, "type", text="${msg}")])
    p = os.path.join(tmp_path, "f.clirec")
    write(rec, p)
    return p


def test_rec_validate_ok(tmp_path, capsys):
    p = _mk(tmp_path)
    cli.cmd_rec(["validate", p])
    assert "OK" in capsys.readouterr().out


def test_rec_validate_failure_exits_nonzero(tmp_path):
    path = tmp_path / "broken.clirec"
    path.write_text("not a recording", encoding="utf-8")
    with pytest.raises(SystemExit) as exc:
        cli.cmd_rec(["validate", str(path)])
    assert exc.value.code == 1


def test_rec_list(tmp_path, capsys):
    _mk(tmp_path)
    cli.cmd_rec(["list", "--dir", str(tmp_path)])
    assert "f.clirec" in capsys.readouterr().out


def test_run_replay_with_fake_executor(tmp_path):
    p = _mk(tmp_path)

    class FakeExec:
        width = 1000
        height = 500

        def __init__(self):
            self.executed = []

        def execute(self, a):
            self.executed.append(a)
            return None

    ex = FakeExec()
    rep = cli._run_replay(p, {"msg": "hello"}, ex)
    assert rep.ok == 1 and ex.executed[0].text == "hello"


def test_rec_replay_failure_exits_nonzero(tmp_path):
    p = _mk(tmp_path)

    class FailingExec:
        width = 1000
        height = 500

        def execute(self, action):
            raise RuntimeError("blocked")

    with pytest.raises(SystemExit) as exc:
        cli.cmd_rec(["replay", p, "--param", "msg=hello"], executor_factory=FailingExec)
    assert exc.value.code == 1


def test_live_recording_is_safe_without_optional_uia_probe(monkeypatch):
    class MissingProbe:
        def available(self):
            return False

    captured = {}

    class FakeRecorder:
        def __init__(self, backend, *, config, **kwargs):
            captured["mask"] = config.mask_password_fields

        def start(self, name):
            pass

        def pump(self):
            raise KeyboardInterrupt

        def stop(self):
            return Recording("demo", "now", "host", "100x100")

        def save(self, recording, name):
            return "demo.clirec"

    monkeypatch.setattr("clirec.capture.base.get_backend", lambda: object())
    monkeypatch.setattr(
        "clirec.capture.base.get_desktop_geometry", lambda: (0, 0, 100, 100)
    )
    monkeypatch.setattr("clirec.uia_probe.DefaultProbe", MissingProbe)
    monkeypatch.setattr("clirec.recorder.Recorder", FakeRecorder)
    cli._rec_live("start", ["demo"])
    assert captured["mask"] is True


def test_live_recording_requires_explicit_flag_for_plaintext(monkeypatch, capsys):
    captured = {}

    class FakeRecorder:
        def __init__(self, backend, *, config, **kwargs):
            captured["mask"] = config.mask_password_fields

        def start(self, name):
            pass

        def pump(self):
            raise KeyboardInterrupt

        def stop(self):
            return Recording("demo", "now", "host", "100x100")

        def save(self, recording, name):
            return "demo.clirec"

    monkeypatch.setattr("clirec.capture.base.get_backend", lambda: object())
    monkeypatch.setattr(
        "clirec.capture.base.get_desktop_geometry", lambda: (0, 0, 100, 100)
    )
    monkeypatch.setattr("clirec.recorder.Recorder", FakeRecorder)
    cli._rec_live("start", ["demo", "--allow-unmasked-input"])
    assert captured["mask"] is False
    assert "WARNING" in capsys.readouterr().err


def test_live_recording_rejects_bad_name_before_backend_start(monkeypatch):
    backend_requested = False

    def get_backend():
        nonlocal backend_requested
        backend_requested = True
        return object()

    monkeypatch.setattr("clirec.capture.base.get_backend", get_backend)
    with pytest.raises(SystemExit) as exc:
        cli._rec_live("start", ["../escaped"])
    assert exc.value.code == 2
    assert backend_requested is False
