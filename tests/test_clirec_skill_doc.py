import os
import re

ROOT_SKILL = "SKILL.md"
SHIPPED_SKILL = os.path.join("skills", "clirec", "SKILL.md")


def _read(path):
    return open(path, encoding="utf-8").read()


def test_skill_exists_and_has_frontmatter():
    assert os.path.exists(SHIPPED_SKILL)
    text = _read(SHIPPED_SKILL)
    assert text.startswith("---")
    assert re.search(r"name:\s*clirec", text)


def test_both_skill_copies_are_identical():
    """The repository ships the skill twice; the two copies must not drift.

    They did: until 2026-09-03 the shipped copy under ``skills/clirec/`` still
    announced the global pause hotkey as "GEPLANT ... noch nicht verdrahtet"
    and did not mention audio capture at all -- both had shipped in 0.3.0. The
    only test that looked at the file checked the stale copy alone, so nothing
    ever compared them.
    """

    assert _read(ROOT_SKILL) == _read(SHIPPED_SKILL), (
        f"{ROOT_SKILL} and {SHIPPED_SKILL} differ -- copy the canonical "
        f"{ROOT_SKILL} over the shipped one instead of editing them apart"
    )


def test_skill_documents_required_topics():
    text = _read(SHIPPED_SKILL).lower()
    for needle in [
        "clirec start",
        ".clirec",
        "selbst",
        "passwort",
        "referenz",
    ]:
        assert needle in text, f"missing topic: {needle}"


def test_skill_does_not_pin_a_feature_state():
    """Topic checks must not freeze a feature's build state into the test.

    The previous suite required the literal word "Ringpuffer" to be present.
    That word only appeared in the sentence declaring the feature unbuilt, so
    correcting the outdated text would have turned the test red -- the check
    defended exactly what it should have caught.
    """

    text = _read(SHIPPED_SKILL)
    stale = ["noch nicht gebaut", "noch nicht verdrahtet", "GEPLANT"]
    found = [phrase for phrase in stale if phrase in text]
    assert not found, f"skill still announces unbuilt features: {found}"


def test_skill_has_no_ascii_umlaut_substitutes():
    text = _read(SHIPPED_SKILL)
    # German content must use real umlauts, not ae/oe/ue substitutes.
    assert "fuer" not in text and "ueber" not in text
