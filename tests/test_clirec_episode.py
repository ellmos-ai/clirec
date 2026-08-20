import pytest

from clirec.episode import build_review_export, export_episode, route_candidate
from clirec.format import Recording, Step


def _recording():
    return Recording(
        "demo",
        "now",
        "HOST",
        "100x100",
        steps=[Step(1, 0.0, "click", x=1, y=1, btn="left")],
    )


def test_episode_separates_demonstration_hypothesis_and_confirmed_outcome():
    episode = export_episode(
        _recording(),
        goal="Datei speichern",
        expected_outcome="Datei vorhanden",
        actual_outcome="Datei vorhanden",
        outcome_confirmed=True,
        export_consent=True,
        export_class="local-review",
    )
    assert episode["schema"] == "clirec.episode.v1"
    assert episode["demonstration"]["steps"]
    assert episode["outcome"]["confirmed"] is True
    assert "raw_audio" not in episode


@pytest.mark.parametrize(
    ("scheduled", "repeatable", "expected"),
    [(False, True, "skill"), (True, True, "workflow"), (False, False, "briefing")],
)
def test_skill_workflow_routing(scheduled, repeatable, expected):
    assert route_candidate(scheduled=scheduled, repeatable=repeatable) == expected


def test_review_export_enforces_outcome_review_dedup_and_neutralization_gates():
    episode = export_episode(
        _recording(),
        goal="C:\\Users\\Alice\\private.txt speichern",
        expected_outcome="gespeichert",
        actual_outcome="gespeichert",
        outcome_confirmed=True,
        export_consent=True,
        export_class="local-review",
    )
    draft = build_review_export(episode, kind="skill", user_reviewed=False)
    assert draft["status"] == "review_required"
    assert "Alice" not in json_text(draft)
    assert draft["gates"]["dedup"] == "extend-existing-first"

    approved = build_review_export(
        episode, kind="workflow", user_reviewed=True, existing_target="save-workflow"
    )
    assert approved["status"] == "approved-for-extractor"
    assert approved["extractor"] == "workflow-extract"

    episode["outcome"]["confirmed"] = False
    with pytest.raises(ValueError, match="confirmed outcome"):
        build_review_export(episode, kind="skill", user_reviewed=True)


def json_text(value):
    import json

    return json.dumps(value, ensure_ascii=False)
