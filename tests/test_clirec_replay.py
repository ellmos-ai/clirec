import pytest

from clirec.format import Recording, Step
from clirec.replay import ReplayAction, ReplayNotExecutedError, replay


class FakeExec:
    width = 1000
    height = 500
    def __init__(self, fail_points=None):
        self.executed = []
        self._fail_points = fail_points or set()
    def execute(self, action: ReplayAction):
        # Fail if this normalized x is configured to fail
        if action.x is not None and round(action.x, 3) in self._fail_points:
            raise ReplayNotExecutedError("element not found")
        self.executed.append(action)
        return None


def test_dumb_replay_executes_all_steps():
    rec = Recording("t", "now", "H", "1000x500", steps=[
        Step(1, 0.0, "click", x=500, y=250, btn="left"),
        Step(2, 0.1, "type", text="hi"),
        Step(3, 0.2, "key", keys="enter"),
    ])
    ex = FakeExec()
    rep = replay(rec, ex)
    assert rep.total == 3 and rep.ok == 3 and rep.failures == []
    assert ex.executed[0].type == "left_click"
    assert abs(ex.executed[0].x - 0.5) < 1e-6  # 500/1000
    assert ex.executed[1].type == "type" and ex.executed[1].text == "hi"
    assert ex.executed[2].type == "key"


def test_param_substitution_in_replay():
    rec = Recording("t", "now", "H", "1000x500", steps=[
        Step(1, 0.0, "type", text="${msg}")])
    ex = FakeExec()
    replay(rec, ex, params={"msg": "hello"})
    assert ex.executed[0].text == "hello"


def test_param_default_is_used_in_replay():
    rec = Recording(
        "t",
        "now",
        "H",
        "1000x500",
        params=[{"name": "msg", "default": "hello"}],
        steps=[Step(1, 0.0, "type", text="${msg}")],
    )
    ex = FakeExec()
    replay(rec, ex)
    assert ex.executed[0].text == "hello"


def test_adaptive_fallback_used_when_dumb_fails():
    rec = Recording("t", "now", "H", "1000x500", steps=[
        Step(1, 0.0, "click", x=500, y=250, btn="left")])
    ex = FakeExec(fail_points={0.5})  # dumb (0.5) fails
    rep = replay(rec, ex, locate=lambda step: (0.8, 0.8))  # relocated
    assert rep.ok == 1 and rep.fallbacks == 1 and rep.failures == []
    assert abs(ex.executed[-1].x - 0.8) < 1e-6


def test_locator_failure_is_reported_without_escaping():
    rec = Recording(
        "t", "now", "H", "1000x500",
        steps=[Step(1, 0.0, "click", x=500, y=250, btn="left")],
    )
    ex = FakeExec(fail_points={0.5})

    def broken_locator(step):
        raise RuntimeError("locator unavailable")

    report = replay(rec, ex, locate=broken_locator)
    assert report.ok == 0
    assert report.failures == ["step 1 locator: locator unavailable"]


def test_failure_recorded_when_both_paths_fail():
    rec = Recording("t", "now", "H", "1000x500", steps=[
        Step(1, 0.0, "click", x=500, y=250, btn="left")])
    ex = FakeExec(fail_points={0.5, 0.8})
    rep = replay(rec, ex, locate=lambda step: (0.8, 0.8))
    assert rep.ok == 0 and len(rep.failures) == 1


def test_replay_stops_after_first_failed_step_by_default():
    rec = Recording(
        "t",
        "now",
        "H",
        "1000x500",
        steps=[
            Step(1, 0.0, "click", x=500, y=250, btn="left"),
            Step(2, 0.1, "type", text="must-not-run"),
        ],
    )
    ex = FakeExec(fail_points={0.5})
    rep = replay(rec, ex)
    assert rep.total == 1
    assert rep.ok == 0
    assert len(rep.failures) == 1
    assert ex.executed == []


def test_replay_can_explicitly_continue_after_failure():
    rec = Recording(
        "t",
        "now",
        "H",
        "1000x500",
        steps=[
            Step(1, 0.0, "click", x=500, y=250, btn="left"),
            Step(2, 0.1, "type", text="continue"),
        ],
    )
    ex = FakeExec(fail_points={0.5})
    rep = replay(rec, ex, continue_on_error=True)
    assert rep.total == 2 and rep.ok == 1 and len(rep.failures) == 1
    assert ex.executed[-1].text == "continue"


def test_generic_exception_is_never_retried_after_possible_side_effect():
    class SideEffectThenError:
        width = 1000
        height = 500

        def __init__(self):
            self.calls = 0

        def execute(self, action):
            self.calls += 1
            raise RuntimeError("effect may already have happened")

    rec = Recording(
        "t",
        "now",
        "H",
        "1000x500",
        steps=[Step(1, 0.0, "click", x=500, y=250, btn="left")],
    )
    ex = SideEffectThenError()
    rep = replay(rec, ex, locate=lambda step: (0.8, 0.8))
    assert ex.calls == 1
    assert rep.fallbacks == 0 and len(rep.failures) == 1


def test_replay_preserves_inter_step_timing_with_injected_sleep():
    rec = Recording(
        "t",
        "now",
        "H",
        "1x1",
        steps=[
            Step(1, 1.5, "type", text="a"),
            Step(2, 2.0, "type", text="b"),
        ],
    )
    delays = []
    replay(rec, FakeExec(), sleep=delays.append)
    assert delays == [1.5, 0.5]


def test_replay_rejects_excessive_delay_before_executor_use():
    rec = Recording("t", "now", "H", "1x1", steps=[Step(1, 61.0, "type", text="a")])
    ex = FakeExec()
    with pytest.raises(ValueError, match="exceeds max_delay"):
        replay(rec, ex)
    assert ex.executed == []


def test_replay_rejects_excessive_total_duration_before_executor_use():
    rec = Recording(
        "t",
        "now",
        "H",
        "1x1",
        steps=[Step(index, index * 60.0, "type", text="a") for index in range(1, 62)],
    )
    ex = FakeExec()
    with pytest.raises(ValueError, match="exceeds max_duration"):
        replay(rec, ex)
    assert ex.executed == []


def test_replay_accounts_for_virtual_desktop_origin():
    rec = Recording(
        "t",
        "now",
        "H",
        "1000x500",
        origin_x=-1000,
        origin_y=-200,
        steps=[Step(1, 0.0, "click", x=-500, y=50, btn="left")],
    )
    ex = FakeExec()
    replay(rec, ex)
    assert ex.executed[0].x == 0.5
    assert ex.executed[0].y == 0.5


@pytest.mark.parametrize("text", ["***", "${missing}"])
def test_replay_rejects_non_replayable_text_before_executor_use(text):
    rec = Recording("t", "now", "H", "1x1", steps=[Step(1, 0.0, "type", text=text)])
    ex = FakeExec()
    with pytest.raises(ValueError, match="not replayable"):
        replay(rec, ex)
    assert ex.executed == []
