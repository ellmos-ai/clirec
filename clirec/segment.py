"""Turn a flat RawEvent stream into semantic clirec Steps.

Pure standard library. UIA enrichment is optional (probe may be None).
"""

from __future__ import annotations

from typing import Protocol, runtime_checkable

from .capture.base import RawEvent
from .format import Step

_DRAG_THRESHOLD_PX = 5
_MODIFIERS = {
    "ctrl": "ctrl", "ctrl_l": "ctrl", "ctrl_r": "ctrl",
    "alt": "alt", "alt_l": "alt", "alt_r": "alt",
    "alt_gr": "altgr",
    "shift": "shift", "shift_l": "shift", "shift_r": "shift",
    "cmd": "win", "cmd_l": "win", "cmd_r": "win", "win": "win",
    "win_l": "win", "win_r": "win",
}
_MODIFIER_ORDER = ("ctrl", "alt", "shift", "win")


@runtime_checkable
class UiaProbeLike(Protocol):
    def element_at(self, x: int, y: int) -> dict | None: ...
    def is_password_focused(self) -> bool: ...


def _enrich(step: Step, event: RawEvent, probe, x, y) -> Step:
    if event.ui_captured or any(
        value is not None for value in (event.ui_name, event.ui_window, event.ui_role)
    ):
        step.ui_name = event.ui_name
        step.ui_window = event.ui_window
        step.ui_role = event.ui_role
        return step
    if probe is None or x is None or y is None:
        return step
    try:
        el = probe.element_at(x, y)
    except Exception:
        el = None
    if el:
        step.ui_name = el.get("name")
        step.ui_window = el.get("window")
        step.ui_role = el.get("role")
    return step


def _password_state(events: list[RawEvent], probe) -> bool | None:
    captured = [event for event in events if event.sensitive_captured]
    if captured:
        states = [event.sensitive for event in captured]
        if any(state is True for state in states):
            return True
        if all(state is False for state in states):
            return False
        return None
    if probe is None:
        # Library callers that deliberately omit a probe retain the historical
        # plaintext behavior. The live CLI always supplies DefaultProbe, whose
        # unknown state still masks fail-closed.
        return False
    state_method = getattr(probe, "password_focus_state", None)
    try:
        if state_method is not None:
            state = state_method()
            return state if state in (True, False) else None
        return bool(probe.is_password_focused())
    except Exception:
        return None


def events_to_steps(events, *, probe=None, mask_passwords: bool = True) -> list[Step]:
    steps: list[Step] = []
    idx = 0
    i = 0
    n = len(events)
    pending_down: RawEvent | None = None
    held_modifiers: dict[str, str] = {}

    def add(step: Step) -> None:
        nonlocal idx
        idx += 1
        step.index = idx
        steps.append(step)

    while i < n:
        e = events[i]
        if e.kind == "mouse_down":
            if pending_down is not None:
                raise ValueError("overlapping mouse buttons are not supported")
            pending_down = e
            i += 1
            continue
        if e.kind == "mouse_up" and pending_down is not None:
            d = pending_down
            pending_down = None
            if e.button != d.button:
                raise ValueError("mouse button changed between down and up")
            dx = abs((e.x or 0) - (d.x or 0))
            dy = abs((e.y or 0) - (d.y or 0))
            if dx <= _DRAG_THRESHOLD_PX and dy <= _DRAG_THRESHOLD_PX:
                s = Step(
                    index=0,
                    t=d.t,
                    action="click",
                    x=d.x,
                    y=d.y,
                    btn=d.button,
                    frame=d.frame,
                )
            else:
                if d.button != "left":
                    raise ValueError(f"unsupported drag button: {d.button!r}")
                s = Step(index=0, t=d.t, action="left_click_drag",
                         x=d.x, y=d.y, end_x=e.x, end_y=e.y, btn=d.button,
                         frame=d.frame)
            add(_enrich(s, d, probe, d.x, d.y))
            i += 1
            continue
        if e.kind == "char":
            j = i
            char_events: list[RawEvent] = []
            while j < n:
                current = events[j]
                if current.kind == "char":
                    char_events.append(current)
                    j += 1
                    continue
                if (
                    current.kind == "key_up"
                    and current.key
                    and current.key.lower() not in _MODIFIERS
                ):
                    j += 1
                    continue
                break
            buf = [event.char or "" for event in char_events]
            text = "".join(buf)
            if mask_passwords and _password_state(char_events, probe) is not False:
                text = "***"
            add(Step(index=0, t=e.t, action="type", text=text))
            i = j
            continue
        if e.kind == "wheel":
            amt = abs(e.delta or 0)
            if amt == 0:
                i += 1
                continue
            direction = "up" if (e.delta or 0) > 0 else "down"
            add(_enrich(Step(index=0, t=e.t, action="scroll", x=e.x, y=e.y,
                             scroll_dir=direction, scroll_amount=amt), e, probe, e.x, e.y))
            i += 1
            continue
        if e.kind == "key_down" and e.key:
            raw_key = e.key.lower()
            modifier = _MODIFIERS.get(raw_key)
            if modifier:
                held_modifiers[raw_key] = modifier
                i += 1
                continue
            active_modifiers = set(held_modifiers.values())
            is_altgr_text = "altgr" in active_modifiers or {
                "ctrl", "alt"
            } <= active_modifiers
            is_shortcut = bool(
                active_modifiers & {"ctrl", "alt", "win"}
            ) and not is_altgr_text
            if (
                mask_passwords
                and len(raw_key) == 1
                and not is_shortcut
                and _password_state([e], probe) is not False
            ):
                add(Step(index=0, t=e.t, action="type", text="***"))
                i += 1
                continue
            key = raw_key
            if held_modifiers:
                active = set(held_modifiers.values())
                prefix = [name for name in _MODIFIER_ORDER if name in active]
                key = "+".join((*prefix, key))
            add(Step(index=0, t=e.t, action="key", keys=key))
            i += 1
            continue
        if e.kind == "key_up" and e.key:
            held_modifiers.pop(e.key.lower(), None)
            i += 1
            continue
        i += 1  # ignore mouse_move / key_up / stray events
    return steps
