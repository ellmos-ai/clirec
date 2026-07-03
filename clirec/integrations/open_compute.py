"""Adapter from clirec replay actions to open-compute actions."""

from __future__ import annotations

from clirec.replay import ReplayAction


def to_open_compute_action(action: ReplayAction):
    """Convert a neutral clirec ``ReplayAction`` to ``open_compute.actions.Action``."""

    from open_compute.actions import Action, ActionType

    return Action(
        type=ActionType(action.type),
        x=action.x,
        y=action.y,
        end_x=action.end_x,
        end_y=action.end_y,
        text=action.text,
        scroll_direction=action.scroll_direction,
        scroll_amount=action.scroll_amount,
    )


class OpenComputeExecutorAdapter:
    """Wrap an open-compute Executor so clirec can replay against it."""

    def __init__(self, executor):
        self._executor = executor

    @property
    def width(self) -> int:
        return self._executor.width

    @property
    def height(self) -> int:
        return self._executor.height

    def execute(self, action: ReplayAction):
        return self._executor.execute(to_open_compute_action(action))
