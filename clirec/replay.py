"""Replay a Recording against an Executor: dumb-first, adaptive fallback.

Pure standard library. The executor is any object with ``width``, ``height``,
and ``execute(ReplayAction)``. Host projects such as open-compute can wrap their
own action types in a tiny adapter without making clirec depend on them.
"""

from __future__ import annotations

import math
import time as time_module
from dataclasses import dataclass, field

from .format import Recording, Step, apply_params, recording_problems

_CLICK_BTN = {
    "left": "left_click",
    "right": "right_click",
    "middle": "middle_click",
}


@dataclass
class ReplayAction:
    """Neutral replay action emitted from a ``.clirec`` step."""

    type: str
    x: float | None = None
    y: float | None = None
    end_x: float | None = None
    end_y: float | None = None
    text: str | None = None
    scroll_direction: str | None = None
    scroll_amount: int | None = None


class ReplayNotExecutedError(RuntimeError):
    """Signal that an action had no side effect and may be relocated safely."""


@dataclass
class ReplayReport:
    total: int = 0
    ok: int = 0
    fallbacks: int = 0
    failures: list[str] = field(default_factory=list)


def _norm(px: int, span: int) -> float:
    if span <= 0:
        return 0.0
    return max(0.0, min(1.0, px / span))


def _res(rec: Recording) -> tuple[int, int]:
    try:
        w, h = rec.resolution.lower().split("x")
        return int(w), int(h)
    except Exception:
        return (0, 0)


def _to_action(step: Step, nx: float | None, ny: float | None,
               end: tuple[float | None, float | None] = (None, None)) -> ReplayAction:
    a = step.action
    if a == "click":
        return ReplayAction(_CLICK_BTN.get(step.btn or "left", "left_click"), x=nx, y=ny)
    if a == "left_click_drag":
        return ReplayAction("left_click_drag", x=nx, y=ny, end_x=end[0], end_y=end[1])
    if a == "type":
        return ReplayAction("type", text=step.text or "")
    if a == "key":
        return ReplayAction("key", text=step.keys or "")
    if a == "scroll":
        return ReplayAction(
            "scroll",
            x=nx,
            y=ny,
            scroll_direction=step.scroll_dir or "down",
            scroll_amount=step.scroll_amount or 1,
        )
    raise ValueError(f"unsupported action for replay: {a!r}")


def _location(value) -> tuple[float, float]:
    if not isinstance(value, (tuple, list)) or len(value) != 2:
        raise ValueError("locator must return a normalized (x, y) pair")
    x, y = value
    if (
        not isinstance(x, (int, float))
        or isinstance(x, bool)
        or not math.isfinite(x)
        or not isinstance(y, (int, float))
        or isinstance(y, bool)
        or not math.isfinite(y)
        or not 0.0 <= x <= 1.0
        or not 0.0 <= y <= 1.0
    ):
        raise ValueError("locator coordinates must be finite and normalized")
    return float(x), float(y)


def replay(
    rec: Recording,
    executor,
    *,
    params=None,
    locate=None,
    continue_on_error: bool = False,
    respect_timing: bool = True,
    max_delay: float = 60.0,
    max_duration: float = 3600.0,
    sleep=None,
) -> ReplayReport:
    """Replay *rec* against *executor*, returning a :class:`ReplayReport`.

    Args:
        rec: The recording to replay.
        executor: Object with ``width``, ``height``, and ``execute(Action)`` method.
        params: Optional substitution dict applied via :func:`apply_params`.
        locate: Optional callable ``(step) -> (float, float) | None`` that
            returns a normalized point when the UIA element is re-found; used
            as adaptive fallback when dumb coordinate execution fails.
        continue_on_error: Continue with later actions after a failed step.
            The safe default is ``False`` because later actions may depend on
            the failed UI transition.
        respect_timing: Preserve recorded inter-step delays.
        max_delay: Reject recordings with a larger inter-step delay before any
            executor action is attempted.
        max_duration: Reject recordings whose full timeline exceeds this many
            seconds before any executor action is attempted.
        sleep: Injectable sleep callable for deterministic tests.

    Returns:
        A :class:`ReplayReport` with total/ok/fallbacks/failures counts.
    """
    rec = apply_params(rec, params or {})
    problems = recording_problems(rec, require_replayable=True)
    if problems:
        raise ValueError("recording is not replayable: " + "; ".join(problems))
    if (
        not isinstance(max_delay, (int, float))
        or isinstance(max_delay, bool)
        or not math.isfinite(max_delay)
        or max_delay < 0
    ):
        raise ValueError("max_delay must be a finite non-negative number")
    if (
        not isinstance(max_duration, (int, float))
        or isinstance(max_duration, bool)
        or not math.isfinite(max_duration)
        or max_duration < 0
    ):
        raise ValueError("max_duration must be a finite non-negative number")
    duration = float(rec.steps[-1].t) if rec.steps else 0.0
    if duration > max_duration:
        raise ValueError(
            f"recording is not replayable: duration {duration:g}s "
            f"exceeds max_duration {max_duration:g}s"
        )
    previous_time = 0.0
    for step in rec.steps:
        delay = float(step.t) - previous_time
        if delay > max_delay:
            raise ValueError(
                f"recording is not replayable: step {step.index} delay {delay:g}s "
                f"exceeds max_delay {max_delay:g}s"
            )
        previous_time = float(step.t)

    sleep_fn = sleep or time_module.sleep
    rw, rh = _res(rec)
    report = ReplayReport()
    previous_time = 0.0
    for step in rec.steps:
        report.total += 1
        if respect_timing:
            delay = float(step.t) - previous_time
            if delay > 0:
                sleep_fn(delay)
        previous_time = float(step.t)
        nx = _norm(step.x - rec.origin_x, rw) if step.x is not None else None
        ny = _norm(step.y - rec.origin_y, rh) if step.y is not None else None
        enx = _norm(step.end_x - rec.origin_x, rw) if step.end_x is not None else None
        eny = _norm(step.end_y - rec.origin_y, rh) if step.end_y is not None else None
        try:
            executor.execute(_to_action(step, nx, ny, end=(enx, eny)))
            report.ok += 1
            continue
        except Exception as first_exc:
            can_retry = isinstance(first_exc, ReplayNotExecutedError) or (
                getattr(first_exc, "clirec_safe_to_retry", False) is True
            )
            relocated = None
            if can_retry and locate is not None and step.x is not None:
                try:
                    candidate = locate(step)
                    relocated = None if candidate is None else _location(candidate)
                except Exception as locator_exc:
                    report.failures.append(f"step {step.index} locator: {locator_exc}")
                    if continue_on_error:
                        continue
                    break
            if relocated is not None:
                try:
                    relocated_end = (enx, eny)
                    if (
                        step.action == "left_click_drag"
                        and nx is not None
                        and ny is not None
                        and enx is not None
                        and eny is not None
                    ):
                        relocated_end = _location(
                            (relocated[0] + enx - nx, relocated[1] + eny - ny)
                        )
                    executor.execute(
                        _to_action(step, relocated[0], relocated[1], end=relocated_end)
                    )
                    report.ok += 1
                    report.fallbacks += 1
                    continue
                except Exception as second_exc:
                    report.failures.append(f"step {step.index}: {second_exc}")
                    if continue_on_error:
                        continue
                    break
            report.failures.append(f"step {step.index}: {first_exc}")
            if not continue_on_error:
                break
    return report
