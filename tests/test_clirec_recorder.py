import os
from pathlib import Path

from clirec.capture.base import RawEvent
from clirec.capture.mock import MockCaptureBackend
from clirec.format import Step
from clirec.recorder import Recorder, RecorderConfig
import pytest


class Clock:
    def __init__(self):
        self.t = 0.0

    def __call__(self):
        return self.t


def test_start_pump_stop_produces_recording(tmp_path):
    evts = [
        RawEvent("mouse_down", 0.0, x=5, y=6, button="left"),
        RawEvent("mouse_up", 0.0, x=5, y=6, button="left"),
    ]
    be = MockCaptureBackend(evts)
    rec = Recorder(
        be,
        config=RecorderConfig(recordings_dir=str(tmp_path)),
        host="LAPTOP",
        resolution="1920x1080",
    )
    rec.start("demo")
    rec.pump()
    out = rec.stop()
    assert out.title == "demo" and out.resolution == "1920x1080"
    assert len(out.steps) == 1 and out.steps[0].action == "click"


def test_save_writes_file(tmp_path):
    be = MockCaptureBackend([RawEvent("char", 0.0, char="x")])
    rec = Recorder(be, config=RecorderConfig(recordings_dir=str(tmp_path)))
    rec.start("t")
    rec.pump()
    out = rec.stop()
    path = rec.save(out, "myflow")
    assert path.endswith("myflow.clirec")
    import os

    assert os.path.exists(path)


def test_ringbuffer_cut_last_keeps_recent(tmp_path):
    clk = Clock()
    be = MockCaptureBackend([])
    rec = Recorder(
        be,
        config=RecorderConfig(
            ringbuffer_enabled=True,
            ringbuffer_minutes=1,
            recordings_dir=str(tmp_path),
            mask_password_fields=False,
        ),
        clock=clk,
    )
    rec.start("buf")
    # inject an old char then a new char via two pumps with advancing clock
    be._events = [RawEvent("char", clk.t, char="old")]
    rec.pump()
    clk.t = 120.0  # 2 minutes later
    be._events = [RawEvent("char", clk.t, char="new")]
    rec.pump()
    out = rec.cut_last(1.0, "recent")  # keep last 1 minute
    joined = "".join(s.text or "" for s in out.steps)
    assert "new" in joined and "old" not in joined


def test_set_paused_delegates():
    be = MockCaptureBackend([RawEvent("char", 0.0, char="a")])
    rec = Recorder(be, config=RecorderConfig())
    rec.start("p")
    rec.set_paused(True)
    rec.pump()
    out = rec.stop()
    assert out.steps == []


def test_start_clears_pause_state_from_previous_session():
    backend = MockCaptureBackend([])
    recorder = Recorder(backend, config=RecorderConfig(mask_password_fields=False))
    recorder.start("one")
    recorder.set_paused(True)
    recorder.stop()
    backend._events = [RawEvent("char", 0.0, char="visible")]
    recorder.start("two")
    recorder.pump()
    assert recorder.stop().steps[0].text == "visible"


def test_recorder_preserves_event_metadata_and_frame_evidence(tmp_path):
    be = MockCaptureBackend(
        [
            RawEvent(
                "mouse_down",
                0.0,
                x=5,
                y=6,
                button="left",
                ui_name="OK",
                ui_window="Dialog",
                ui_role="button",
            ),
            RawEvent("mouse_up", 0.1, x=5, y=6, button="left"),
        ]
    )
    rec = Recorder(
        be,
        config=RecorderConfig(recordings_dir=str(tmp_path)),
        frame_grabber=lambda: b"PNG-EVIDENCE",
        resolution="100x100",
    )
    rec.start("evidence")
    rec.pump()
    out = rec.stop()
    assert out.steps[0].ui_name == "OK"
    assert out.steps[0].frame == "0001.png"
    assert out._frame_data == {"0001.png": b"PNG-EVIDENCE"}

    path = rec.save(out, "evidence")
    frames_dir = path + ".frames"
    assert (
        tmp_path / "evidence.clirec.frames" / "0001.png"
    ).read_bytes() == b"PNG-EVIDENCE"
    assert frames_dir.endswith("evidence.clirec.frames")


def test_password_state_is_bound_when_events_are_pumped():
    class MutableProbe:
        state = True

        def password_focus_state(self):
            return self.state

    probe = MutableProbe()
    be = MockCaptureBackend([RawEvent("char", 0.0, char="secret")])
    rec = Recorder(be, config=RecorderConfig(), probe=probe)
    rec.start("privacy")
    rec.pump()
    probe.state = False
    out = rec.stop()
    assert out.steps[0].text == "${input_1}"
    assert out.params == [
        {"name": "input_1", "desc": "Masked keyboard input for step 1"}
    ]


def test_backend_can_bind_password_state_at_event_time_before_delayed_pump():
    class EventTimeBackend(MockCaptureBackend):
        def emit_char(self, value):
            state = self._sensitive_provider() if self._sensitive_provider else None
            self._events.append(
                RawEvent(
                    "char",
                    0.0,
                    char=value,
                    sensitive=state,
                    sensitive_captured=True,
                )
            )

    class MutableProbe:
        state = True

        def password_focus_state(self):
            return self.state

    probe = MutableProbe()
    backend = EventTimeBackend([])
    recorder = Recorder(backend, config=RecorderConfig(), probe=probe)
    recorder.start("privacy")
    backend.emit_char("secret")
    probe.state = False
    recorder.pump()
    assert recorder.stop().steps[0].text == "${input_1}"


def test_safe_default_masks_text_without_calling_probe_from_backend():
    class ExplodingProbe:
        def password_focus_state(self):
            raise AssertionError("input callback must never call the privacy probe")

    backend = MockCaptureBackend([])
    recorder = Recorder(backend, config=RecorderConfig(), probe=ExplodingProbe())
    recorder.start("safe")
    assert backend._sensitive_provider() is True
    backend._events = [
        RawEvent(
            "char",
            0.0,
            char="never-persist",
            sensitive=False,
            sensitive_captured=True,
        )
    ]
    recorder.pump()
    assert recorder.stop().steps[0].text == "${input_1}"


def test_safe_default_preserves_ctrl_shortcuts_but_parameterizes_altgr_text():
    backend = MockCaptureBackend(
        [
            RawEvent("key_down", 0.0, key="ctrl_l"),
            RawEvent("key_down", 0.1, key="c"),
            RawEvent("key_up", 0.2, key="c"),
            RawEvent("key_up", 0.3, key="ctrl_l"),
            RawEvent("key_down", 0.4, key="ctrl_l"),
            RawEvent("key_down", 0.5, key="alt_r"),
            RawEvent("key_down", 0.6, key="@"),
            RawEvent("key_up", 0.7, key="@"),
            RawEvent("key_up", 0.8, key="alt_r"),
            RawEvent("key_up", 0.9, key="ctrl_l"),
        ]
    )
    recorder = Recorder(backend, config=RecorderConfig())
    recorder.start("keys")
    recorder.pump()
    out = recorder.stop()
    assert out.steps[0].action == "key" and out.steps[0].keys == "ctrl+c"
    assert out.steps[1].action == "type" and out.steps[1].text == "${input_1}"


def test_ui_metadata_is_bound_when_event_is_pumped():
    class MutableProbe:
        name = "clicked-control"

        def element_at(self, x, y):
            return {"name": self.name, "window": "Window", "role": "button"}

    probe = MutableProbe()
    backend = MockCaptureBackend(
        [
            RawEvent("mouse_down", 0.0, x=1, y=1, button="left"),
            RawEvent("mouse_up", 0.1, x=1, y=1, button="left"),
        ]
    )
    recorder = Recorder(
        backend, config=RecorderConfig(), probe=probe, resolution="10x10"
    )
    recorder.start("metadata")
    recorder.pump()
    probe.name = "different-control-at-stop"
    assert recorder.stop().steps[0].ui_name == "clicked-control"


def test_stop_always_releases_backend_when_segmentation_fails():
    be = MockCaptureBackend(
        [
            RawEvent("mouse_down", 0.0, x=1, y=1, button="left"),
            RawEvent("mouse_down", 0.1, x=2, y=2, button="left"),
        ]
    )
    rec = Recorder(be, config=RecorderConfig(capture_screenshots=False))
    rec.start("broken")
    rec.pump()
    with pytest.raises(ValueError, match="overlapping mouse buttons"):
        rec.stop()
    assert be._started is False


def test_failed_backend_stop_remains_retryable():
    class RetryStopBackend(MockCaptureBackend):
        def __init__(self):
            super().__init__([])
            self.stop_calls = 0

        def stop(self):
            self.stop_calls += 1
            if self.stop_calls == 1:
                raise RuntimeError("thread did not stop")
            super().stop()

    backend = RetryStopBackend()
    recorder = Recorder(backend, config=RecorderConfig())
    recorder.start("retry")
    with pytest.raises(RuntimeError, match="did not stop"):
        recorder.stop()
    assert recorder._running is True
    recorder.stop()
    assert backend.stop_calls == 2
    assert recorder._running is False


@pytest.mark.parametrize(
    "name",
    ["../escaped", "..\\escaped", "..", "a/b", "a:b", "CON", "LPT9.txt", "trail."],
)
def test_save_rejects_names_that_escape_recordings_dir(tmp_path, name):
    rec = Recorder(
        MockCaptureBackend([]), config=RecorderConfig(recordings_dir=str(tmp_path))
    )
    model = rec._build([])
    with pytest.raises(ValueError, match="local filename"):
        rec.save(model, name)


def test_save_is_no_overwrite_and_leaves_no_orphan_frames_on_validation_error(tmp_path):
    rec = Recorder(
        MockCaptureBackend([]), config=RecorderConfig(recordings_dir=str(tmp_path))
    )
    rec._title = "valid"
    valid = rec._build([])
    rec.save(valid, "same")
    with pytest.raises(FileExistsError):
        rec.save(valid, "same")

    invalid = rec._build([])
    invalid.resolution = "broken"
    invalid.steps = [Step(1, 0.0, "click", x=1, y=1, btn="left", frame="0001.png")]
    invalid._frame_data = {"0001.png": b"PNG"}
    with pytest.raises(ValueError):
        rec.save(invalid, "invalid")
    assert not (tmp_path / "invalid.clirec").exists()
    assert not (tmp_path / "invalid.clirec.frames").exists()


def test_save_rejects_missing_and_orphan_frame_evidence(tmp_path):
    recorder = Recorder(
        MockCaptureBackend([]), config=RecorderConfig(recordings_dir=str(tmp_path))
    )
    recorder._title = "frames"

    missing = recorder._build([])
    missing.steps = [Step(1, 0.0, "click", x=1, y=1, btn="left", frame="missing.png")]
    with pytest.raises(ValueError, match="missing frame data"):
        recorder.save(missing, "missing")

    orphan = recorder._build([])
    orphan._frame_data = {"orphan.png": b"PNG"}
    with pytest.raises(ValueError, match="orphan frame data"):
        recorder.save(orphan, "orphan")


def test_save_never_publishes_an_empty_recording(tmp_path, monkeypatch):
    recorder = Recorder(
        MockCaptureBackend([]), config=RecorderConfig(recordings_dir=str(tmp_path))
    )
    recorder._title = "atomic"
    model = recorder._build([])
    target = tmp_path / "atomic.clirec"
    real_link = os.link

    def observing_link(source, destination):
        assert Path(destination) == target
        assert not target.exists()
        assert Path(source).stat().st_size > 0
        return real_link(source, destination)

    monkeypatch.setattr(os, "link", observing_link)
    recorder.save(model, "atomic")
    assert target.stat().st_size > 0


def test_ringbuffer_prune_releases_unreferenced_frame_bytes(tmp_path):
    clock = Clock()
    be = MockCaptureBackend([])
    rec = Recorder(
        be,
        config=RecorderConfig(
            recordings_dir=str(tmp_path),
            ringbuffer_enabled=True,
            ringbuffer_minutes=1,
        ),
        frame_grabber=lambda: b"frame",
        clock=clock,
    )
    rec.start("buffer")
    be._events = [RawEvent("mouse_down", 0.0, x=1, y=1, button="left")]
    rec.pump()
    assert rec._frames
    clock.t = 120.0
    be._events = [RawEvent("key_down", 120.0, key="enter")]
    rec.pump()
    assert rec._frames == {}


def test_frame_ids_do_not_collide_after_ringbuffer_prune(tmp_path):
    clock = Clock()
    backend = MockCaptureBackend([])
    frame_payloads = iter([b"A", b"B", b"C"])
    recorder = Recorder(
        backend,
        config=RecorderConfig(ringbuffer_enabled=True, ringbuffer_minutes=1),
        frame_grabber=lambda: next(frame_payloads),
        clock=clock,
    )
    recorder.start("frames")
    backend._events = [RawEvent("mouse_down", 0.0, x=1, y=1, button="left")]
    recorder.pump()
    clock.t = 30.0
    backend._events = [RawEvent("mouse_down", 30.0, x=2, y=2, button="left")]
    recorder.pump()
    clock.t = 70.0
    backend._events = [RawEvent("mouse_down", 70.0, x=3, y=3, button="left")]
    recorder.pump()
    assert recorder._frames == {"0002.png": b"B", "0003.png": b"C"}


def test_stop_resets_buffer(tmp_path):
    be = MockCaptureBackend([RawEvent("char", 0.0, char="a")])
    rec = Recorder(be, config=RecorderConfig(recordings_dir=str(tmp_path)))
    rec.start("r")
    rec.pump()
    rec.stop()
    # Second stop without start/pump should yield empty steps
    out = rec.stop()
    assert out.steps == []
