"""Read, write and validate the human-readable ``.clirec`` format."""

from __future__ import annotations

import copy
import json
import math
import os
import re
import stat
import tempfile
from dataclasses import dataclass, field, replace
from pathlib import Path

VERSION = 1
STEPS_MARKER = "--- steps ---"
SUPPORTED_ACTIONS = {"click", "left_click_drag", "type", "key", "scroll"}
_PARAM_NAME = re.compile(r"[A-Za-z_][A-Za-z0-9_-]{0,63}\Z")
_PLACEHOLDER = re.compile(r"\$\{([A-Za-z_][A-Za-z0-9_-]{0,63})\}")
_KV = re.compile(r'(\w+)=("(?:[^"\\]|\\.)*"|\S+)')
_STEP_FIELDS = {
    "x",
    "y",
    "end_x",
    "end_y",
    "btn",
    "text",
    "keys",
    "scroll_dir",
    "scroll_amount",
    "ui",
    "window",
    "role",
    "frame",
}


@dataclass
class Step:
    index: int
    t: float
    action: str
    x: int | None = None
    y: int | None = None
    end_x: int | None = None
    end_y: int | None = None
    btn: str | None = None
    text: str | None = None
    keys: str | None = None
    scroll_dir: str | None = None
    scroll_amount: int | None = None
    ui_name: str | None = None
    ui_window: str | None = None
    ui_role: str | None = None
    frame: str | None = None


@dataclass
class Recording:
    title: str
    created: str
    host: str
    resolution: str
    goal: str = ""
    params: list[dict] = field(default_factory=list)
    steps: list[Step] = field(default_factory=list)
    origin_x: int = 0
    origin_y: int = 0
    _frame_data: dict[str, bytes] = field(
        default_factory=dict, repr=False, compare=False
    )


def _q(value: str) -> str:
    return json.dumps(value, ensure_ascii=False)


def _unq(value: str) -> str:
    if value.startswith('"'):
        parsed = json.loads(value)
        if not isinstance(parsed, str):
            raise ValueError("quoted value must be a string")
        return parsed
    return value


def _single_line(
    value: object, label: str, problems: list[str], *, required: bool = False
) -> None:
    if not isinstance(value, str):
        problems.append(f"{label} must be a string")
    elif "\n" in value or "\r" in value:
        problems.append(f"{label} must be a single line")
    elif required and not value.strip():
        problems.append(f"{label} must not be empty")


def _resolution(value: str) -> tuple[int, int] | None:
    match = re.fullmatch(r"(\d+)x(\d+)", value.lower())
    if not match:
        return None
    width, height = int(match.group(1)), int(match.group(2))
    return (width, height) if width > 0 and height > 0 else None


def recording_problems(
    rec: Recording, *, require_replayable: bool = False
) -> list[str]:
    """Return structural and semantic problems for an in-memory recording."""

    problems: list[str] = []
    _single_line(rec.title, "title", problems, required=True)
    _single_line(rec.created, "created", problems, required=True)
    _single_line(rec.host, "host", problems, required=True)
    _single_line(rec.resolution, "resolution", problems, required=True)
    if not isinstance(rec.origin_x, int) or isinstance(rec.origin_x, bool):
        problems.append("origin_x must be an integer")
    if not isinstance(rec.origin_y, int) or isinstance(rec.origin_y, bool):
        problems.append("origin_y must be an integer")
    if not isinstance(rec.goal, str):
        problems.append("goal must be a string")

    geometry = _resolution(rec.resolution) if isinstance(rec.resolution, str) else None
    parameter_names: set[str] = set()
    if not isinstance(rec.params, list):
        problems.append("params must be a list")
    else:
        for position, parameter in enumerate(rec.params, 1):
            if not isinstance(parameter, dict):
                problems.append(f"param {position} must be an object")
                continue
            name = parameter.get("name")
            if not isinstance(name, str) or not _PARAM_NAME.fullmatch(name):
                problems.append(f"param {position} has an invalid name")
            elif name in parameter_names:
                problems.append(f"duplicate param name: {name}")
            else:
                parameter_names.add(name)
            for key in ("desc", "default"):
                if key in parameter:
                    _single_line(parameter[key], f"param {position} {key}", problems)

    if not isinstance(rec.steps, list):
        problems.append("steps must be a list")
        return problems
    if len(rec.steps) > 10_000:
        problems.append("recording exceeds the 10000-step safety limit")

    previous_t = -1.0
    for position, step in enumerate(rec.steps, 1):
        prefix = f"step {position}"
        if not isinstance(step, Step):
            problems.append(f"{prefix} must be a Step")
            continue
        if step.index != position:
            problems.append(f"{prefix} index must be {position}, got {step.index!r}")
        if (
            not isinstance(step.t, (int, float))
            or isinstance(step.t, bool)
            or not math.isfinite(step.t)
        ):
            problems.append(f"{prefix} time must be finite")
        elif step.t < 0 or step.t < previous_t:
            problems.append(f"{prefix} time must be non-negative and monotonic")
        else:
            previous_t = float(step.t)
        if step.action not in SUPPORTED_ACTIONS:
            problems.append(f"{prefix} has unsupported action: {step.action!r}")

        for field_name in ("ui_name", "ui_window", "ui_role"):
            value = getattr(step, field_name)
            if value is not None:
                _single_line(value, f"{prefix} {field_name}", problems)

        coordinate_names = ("x", "y", "end_x", "end_y")
        for field_name in coordinate_names:
            value = getattr(step, field_name)
            if value is not None and (
                not isinstance(value, int) or isinstance(value, bool)
            ):
                problems.append(f"{prefix} {field_name} must be an integer")
        if (step.x is None) != (step.y is None):
            problems.append(f"{prefix} x and y must appear together")
        if (step.end_x is None) != (step.end_y is None):
            problems.append(f"{prefix} end_x and end_y must appear together")

        if step.action == "click":
            if step.x is None or step.y is None:
                problems.append(f"{prefix} click requires x and y")
            if step.btn not in {"left", "right", "middle"}:
                problems.append(f"{prefix} click has invalid button")
        elif step.action == "left_click_drag":
            if None in (step.x, step.y, step.end_x, step.end_y):
                problems.append(f"{prefix} drag requires start and end coordinates")
            if step.btn not in (None, "left"):
                problems.append(f"{prefix} drag only supports the left button")
        elif step.action == "type":
            if not isinstance(step.text, str):
                problems.append(f"{prefix} type requires text")
            elif require_replayable:
                if step.text == "***":
                    problems.append(
                        f"{prefix} contains masked text without a parameter"
                    )
                unresolved = sorted(set(_PLACEHOLDER.findall(step.text)))
                if unresolved:
                    problems.append(
                        f"{prefix} has unresolved parameters: {', '.join(unresolved)}"
                    )
        elif step.action == "key":
            _single_line(step.keys, f"{prefix} keys", problems, required=True)
        elif step.action == "scroll":
            if step.scroll_dir not in {"up", "down"}:
                problems.append(f"{prefix} scroll direction must be up or down")
            if (
                not isinstance(step.scroll_amount, int)
                or isinstance(step.scroll_amount, bool)
                or step.scroll_amount <= 0
            ):
                problems.append(f"{prefix} scroll amount must be a positive integer")

        if step.frame is not None:
            _single_line(step.frame, f"{prefix} frame", problems, required=True)
            if Path(step.frame).name != step.frame or not step.frame.lower().endswith(
                ".png"
            ):
                problems.append(f"{prefix} frame must be a local PNG filename")

        if geometry is not None:
            width, height = geometry
            for x_name, y_name in (("x", "y"), ("end_x", "end_y")):
                x_value, y_value = getattr(step, x_name), getattr(step, y_name)
                if isinstance(x_value, int) and isinstance(y_value, int):
                    if not rec.origin_x <= x_value < rec.origin_x + width:
                        problems.append(
                            f"{prefix} {x_name} lies outside the recorded desktop"
                        )
                    if not rec.origin_y <= y_value < rec.origin_y + height:
                        problems.append(
                            f"{prefix} {y_name} lies outside the recorded desktop"
                        )
        elif any(getattr(step, name) is not None for name in coordinate_names):
            problems.append(f"{prefix} has coordinates but resolution is not positive")

    return problems


def _raise_if_invalid(rec: Recording, *, require_replayable: bool = False) -> None:
    problems = recording_problems(rec, require_replayable=require_replayable)
    if problems:
        raise ValueError("; ".join(problems))


def _fmt_step(step: Step) -> str:
    head = f"[{step.index:03d}] t={float(step.t):.17g}   {step.action}"
    parts: list[str] = []
    if step.x is not None:
        parts.append(f"x={step.x} y={step.y}")
    if step.end_x is not None:
        parts.append(f"end_x={step.end_x} end_y={step.end_y}")
    if step.btn:
        parts.append(f"btn={step.btn}")
    if step.text is not None:
        parts.append(f"text={_q(step.text)}")
    if step.keys:
        parts.append(f"keys={_q(step.keys)}")
    if step.scroll_dir:
        parts.append(f"scroll_dir={step.scroll_dir} scroll_amount={step.scroll_amount}")
    line = head + ("      " + "  ".join(parts) if parts else "")
    metadata: list[str] = []
    if step.ui_name is not None:
        metadata.append(f"ui={_q(step.ui_name)}")
    if step.ui_window is not None:
        metadata.append(f"window={_q(step.ui_window)}")
    if step.ui_role is not None:
        metadata.append(f"role={_q(step.ui_role)}")
    if step.frame:
        metadata.append(f"frame={_q(step.frame)}")
    return line + ("\n      " + " ".join(metadata) if metadata else "")


def dumps(rec: Recording) -> str:
    _raise_if_invalid(rec)
    output = [
        f"# clirec-version: {VERSION}",
        f"title: {_q(rec.title)}",
        f"created: {_q(rec.created)}",
        f"host: {_q(rec.host)}",
        f"resolution: {_q(rec.resolution)}",
        f"origin: {rec.origin_x},{rec.origin_y}",
    ]
    if rec.goal:
        output.append("goal: |")
        output.extend(f"  {line}" for line in rec.goal.split("\n"))
    if rec.params:
        output.append("params:")
        for parameter in rec.params:
            output.append(f"  - name: {parameter['name']}")
            if "desc" in parameter:
                output.append(f"    desc: {_q(parameter['desc'])}")
            if "default" in parameter:
                output.append(f"    default: {_q(parameter['default'])}")
    output.extend(("", STEPS_MARKER))
    output.extend(_fmt_step(step) for step in rec.steps)
    return "\n".join(output) + "\n"


def _parse_kv(text: str) -> dict[str, str]:
    values: dict[str, str] = {}
    matches = list(_KV.finditer(text))
    remainder = _KV.sub("", text).strip()
    if remainder:
        raise ValueError(f"unparsed step data: {remainder!r}")
    for match in matches:
        key, raw_value = match.groups()
        if key in values:
            raise ValueError(f"duplicate step field: {key}")
        values[key] = _unq(raw_value)
    return values


def _parse_step(line: str, metadata: str | None) -> Step:
    match = re.match(r"\[(\d+)\]\s+t=([^\s]+)\s+([a-z_]+)(.*)\Z", line)
    if not match:
        raise ValueError(f"bad step line: {line!r}")
    values = _parse_kv(match.group(4))
    if metadata:
        extra = _parse_kv(metadata)
        duplicate = values.keys() & extra.keys()
        if duplicate:
            raise ValueError(f"duplicate step field: {sorted(duplicate)[0]}")
        values.update(extra)
    unknown = sorted(values.keys() - _STEP_FIELDS)
    if unknown:
        raise ValueError(f"unknown step field: {unknown[0]}")
    return Step(
        index=int(match.group(1)),
        t=float(match.group(2)),
        action=match.group(3),
        x=int(values["x"]) if "x" in values else None,
        y=int(values["y"]) if "y" in values else None,
        end_x=int(values["end_x"]) if "end_x" in values else None,
        end_y=int(values["end_y"]) if "end_y" in values else None,
        btn=values.get("btn"),
        text=values.get("text"),
        keys=values.get("keys"),
        scroll_dir=values.get("scroll_dir"),
        scroll_amount=int(values["scroll_amount"])
        if "scroll_amount" in values
        else None,
        ui_name=values.get("ui"),
        ui_window=values.get("window"),
        ui_role=values.get("role"),
        frame=values.get("frame"),
    )


def _parse_scalar(value: str) -> str:
    return _unq(value.strip())


def loads(text: str) -> Recording:
    if not isinstance(text, str):
        raise TypeError("clirec input must be text")
    lines = text.splitlines()
    if not lines or lines[0].strip() != f"# clirec-version: {VERSION}":
        raise ValueError(f"unsupported or missing clirec version; expected {VERSION}")
    # Only an unindented marker starts the step section.  An identical line in
    # a block-style goal is data and must survive a dumps/loads round trip.
    markers = [index for index, line in enumerate(lines) if line == STEPS_MARKER]
    if len(markers) != 1:
        raise ValueError("expected exactly one '--- steps ---' section")
    marker_index = markers[0]

    header: dict[str, str] = {}
    goal_lines: list[str] = []
    params: list[dict] = []
    current_param: dict | None = None
    in_goal = False
    in_params = False
    index = 1
    while index < marker_index:
        line = lines[index]
        if in_goal and line.startswith("  "):
            goal_lines.append(line[2:])
            index += 1
            continue
        in_goal = False
        if not line.strip() or line.lstrip().startswith("#"):
            index += 1
            continue
        if in_params and line.startswith("  "):
            stripped = line.strip()
            if stripped.startswith("- name:"):
                current_param = {"name": _parse_scalar(stripped.split(":", 1)[1])}
                params.append(current_param)
            elif current_param is not None and ":" in stripped:
                key, value = stripped.split(":", 1)
                if key.strip() not in {"desc", "default"}:
                    raise ValueError(f"unknown param field: {key.strip()}")
                if key.strip() in current_param:
                    raise ValueError(f"duplicate param field: {key.strip()}")
                current_param[key.strip()] = _parse_scalar(value)
            else:
                raise ValueError(f"bad params line: {line!r}")
            index += 1
            continue
        in_params = False
        if line.strip() == "goal: |":
            in_goal = True
            index += 1
            continue
        if line.strip() == "params:":
            in_params = True
            index += 1
            continue
        if ":" not in line:
            raise ValueError(f"bad header line: {line!r}")
        key, value = line.split(":", 1)
        key = key.strip()
        if key not in {"title", "created", "host", "resolution", "origin"}:
            raise ValueError(f"unknown header: {key}")
        if key in header:
            raise ValueError(f"duplicate header: {key}")
        header[key] = _parse_scalar(value)
        index += 1

    steps: list[Step] = []
    index = marker_index + 1
    while index < len(lines):
        line = lines[index]
        if not line.strip():
            index += 1
            continue
        metadata = None
        if index + 1 < len(lines) and lines[index + 1].startswith("      "):
            metadata = lines[index + 1].strip()
            index += 1
        steps.append(_parse_step(line.strip(), metadata))
        index += 1

    try:
        origin_x, origin_y = (
            int(value) for value in header.get("origin", "0,0").split(",", 1)
        )
    except (TypeError, ValueError) as exc:
        raise ValueError("origin must be two comma-separated integers") from exc
    rec = Recording(
        title=header.get("title", ""),
        created=header.get("created", ""),
        host=header.get("host", ""),
        resolution=header.get("resolution", ""),
        origin_x=origin_x,
        origin_y=origin_y,
        goal="\n".join(goal_lines),
        params=params,
        steps=steps,
    )
    _raise_if_invalid(rec)
    return rec


def write(rec: Recording, path: str | os.PathLike) -> None:
    """Atomically write a validated recording beside any existing target."""

    target = Path(path)
    content = dumps(rec)
    mode = stat.S_IMODE(target.stat().st_mode) if target.exists() else None
    temporary: Path | None = None
    try:
        with tempfile.NamedTemporaryFile(
            mode="w",
            encoding="utf-8",
            newline="\n",
            delete=False,
            dir=target.parent,
            prefix=f".{target.name}.",
            suffix=".tmp",
        ) as handle:
            temporary = Path(handle.name)
            handle.write(content)
            handle.flush()
            os.fsync(handle.fileno())
        if mode is not None:
            os.chmod(temporary, mode)
        os.replace(temporary, target)
    finally:
        if temporary is not None and temporary.exists():
            temporary.unlink()


def read(path: str | os.PathLike) -> Recording:
    with open(path, "r", encoding="utf-8") as handle:
        return loads(handle.read())


def validate(text: str) -> list[str]:
    try:
        loads(text)
    except Exception as exc:
        return [f"parse error: {exc}"]
    return []


def apply_params(rec: Recording, values: dict[str, str]) -> Recording:
    if not isinstance(values, dict):
        raise TypeError("parameter values must be a dictionary")
    for key, value in values.items():
        if not isinstance(key, str) or not _PARAM_NAME.fullmatch(key):
            raise ValueError(f"invalid parameter name: {key!r}")
        if not isinstance(value, str):
            raise TypeError(f"parameter {key!r} must be a string")
    substitutions = {
        parameter["name"]: parameter["default"]
        for parameter in rec.params
        if isinstance(parameter, dict)
        and isinstance(parameter.get("name"), str)
        and isinstance(parameter.get("default"), str)
    }
    substitutions.update(values)
    new_steps: list[Step] = []
    for step in rec.steps:
        new_step = replace(step)
        if new_step.text is not None:
            for key, value in substitutions.items():
                new_step.text = new_step.text.replace("${" + key + "}", value)
        new_steps.append(new_step)
    return replace(
        rec,
        steps=new_steps,
        params=copy.deepcopy(rec.params),
        _frame_data=dict(rec._frame_data),
    )
