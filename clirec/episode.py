"""Privacy-bounded learning episode and extractor review exports."""

from __future__ import annotations

import copy
import re
import uuid
from dataclasses import asdict

from .format import Recording

_WINDOWS_USER = re.compile(r"(?i)[A-Z]:\\Users\\[^\\\s]+")
_POSIX_USER = re.compile(r"/(?:home|Users)/[^/\s]+")


def _neutralize(value):
    if isinstance(value, str):
        value = _WINDOWS_USER.sub("${USER_HOME}", value)
        return _POSIX_USER.sub("${USER_HOME}", value)
    if isinstance(value, list):
        return [_neutralize(item) for item in value]
    if isinstance(value, dict):
        return {key: _neutralize(item) for key, item in value.items()}
    return value


def export_episode(
    recording: Recording,
    *,
    goal: str,
    expected_outcome: str,
    actual_outcome: str,
    outcome_confirmed: bool,
    export_consent: bool,
    export_class: str,
    corrections: list[str] | None = None,
    transcript_segments: list[dict] | None = None,
    references: list[str] | None = None,
) -> dict:
    """Build a local metadata episode; media bytes are never embedded."""

    if not export_consent:
        raise PermissionError("episode export requires explicit consent")
    steps = [asdict(step) for step in recording.steps]
    media_links = [
        {key: item[key] for key in ("kind", "path", "sha256") if key in item}
        for item in recording.media
    ]
    episode = {
        "schema": "clirec.episode.v1",
        "episode_id": uuid.uuid4().hex,
        "provenance": {
            "recording_title": recording.title,
            "recording_created": recording.created,
            "format_version": recording.version,
        },
        "intention": goal,
        "demonstration": {"steps": steps, "media_links": media_links},
        "annotations": copy.deepcopy(transcript_segments or []),
        "expected_outcome": expected_outcome,
        "outcome": {
            "actual": actual_outcome,
            "confirmed": bool(outcome_confirmed),
        },
        "corrections": list(corrections or []),
        "references": list(references or []),
        "consent": {"export": True, "class": export_class},
        "learning_status": "review_required",
    }
    return _neutralize(episode)


def route_candidate(*, scheduled: bool, repeatable: bool) -> str:
    if scheduled and repeatable:
        return "workflow"
    if repeatable:
        return "skill"
    return "briefing"


def build_review_export(
    episode: dict,
    *,
    kind: str,
    user_reviewed: bool,
    existing_target: str | None = None,
) -> dict:
    """Create a machine-readable, review-gated skill/workflow extractor job."""

    if kind not in {"skill", "workflow"}:
        raise ValueError("kind must be 'skill' or 'workflow'")
    if not episode.get("outcome", {}).get("confirmed"):
        raise ValueError("a confirmed outcome is required before extractor routing")
    extractor = "skill-extractor" if kind == "skill" else "workflow-extract"
    gates = {
        "outcome_confirmed": True,
        "user_reviewed": bool(user_reviewed),
        "dedup": "extend-existing-first",
        "neutralization": "required",
        "deployment": "manual-review-only",
    }
    if kind == "workflow":
        gates.update(
            {
                "idempotence": "required",
                "locks": "required",
                "read_only_exit": "required",
                "log_hygiene": "required",
                "schedule_budget": "review-required",
            }
        )
    return _neutralize(
        {
            "schema": "clirec.extractor-review.v1",
            "extractor": extractor,
            "candidate_kind": kind,
            "status": (
                "approved-for-extractor" if user_reviewed else "review_required"
            ),
            "existing_target": existing_target,
            "episode": copy.deepcopy(episode),
            "gates": gates,
        }
    )
