# tests/test_clirec_format.py
from clirec import format as fmt


def _sample() -> fmt.Recording:
    return fmt.Recording(
        title="LinkedIn-Post",
        created="2026-06-28T14:03:11",
        host="LAPTOP",
        resolution="2560x1440",
        goal="Einen Beitrag posten.",
        params=[{"name": "post_text", "desc": "Der Text", "default": ""}],
        steps=[
            fmt.Step(index=1, t=0.0, action="click", x=1180, y=64, btn="left",
                     ui_name="Beitrag starten", ui_window="LinkedIn", ui_role="button",
                     frame="0001.png"),
            fmt.Step(index=2, t=1.42, action="type", text="${post_text}",
                     ui_name="Editor", ui_window="Beitrag", ui_role="edit"),
        ],
    )


def test_roundtrip_preserves_recording():
    rec = _sample()
    text = fmt.dumps(rec)
    back = fmt.loads(text)
    assert back.title == rec.title
    assert back.resolution == "2560x1440"
    assert len(back.steps) == 2
    assert back.steps[0].x == 1180 and back.steps[0].btn == "left"
    assert back.steps[0].ui_name == "Beitrag starten"
    assert back.steps[1].action == "type" and back.steps[1].text == "${post_text}"


def test_roundtrip_preserves_virtual_desktop_origin_and_escaped_text():
    rec = _sample()
    rec.origin_x = -1920
    rec.origin_y = -200
    rec.steps[0].x = -740
    rec.steps[1].text = 'Zeile mit "Quotes" und \\Pfad'
    back = fmt.loads(fmt.dumps(rec))
    assert (back.origin_x, back.origin_y) == (-1920, -200)
    assert back.steps[1].text == rec.steps[1].text


def test_roundtrip_preserves_steps_marker_inside_goal():
    rec = _sample()
    rec.goal = "# Heading\nfirst\n--- steps ---\nlast"
    assert fmt.loads(fmt.dumps(rec)).goal == rec.goal


def test_roundtrip_preserves_padded_headers_trailing_goal_newline_and_float_time():
    rec = _sample()
    rec.title = " padded "
    rec.goal = "line\n"
    rec.steps[0].t = 1234.5678912
    rec.steps[1].t = 1235.0
    back = fmt.loads(fmt.dumps(rec))
    assert back.title == rec.title
    assert back.goal == rec.goal
    assert back.steps[0].t == rec.steps[0].t


def test_parser_rejects_unknown_step_fields():
    text = fmt.dumps(_sample()).replace("btn=left", "btn=left ignored=payload", 1)
    problems = fmt.validate(text)
    assert any("unknown step field" in problem for problem in problems)


def test_frame_filename_with_spaces_roundtrips():
    rec = _sample()
    rec.steps[0].frame = "frame one.png"
    assert fmt.loads(fmt.dumps(rec)).steps[0].frame == "frame one.png"


def test_validate_flags_missing_steps_section():
    problems = fmt.validate("# clirec-version: 1\ntitle: x\n")
    assert any("steps" in p.lower() for p in problems)


def test_validate_ok_returns_empty():
    assert fmt.validate(fmt.dumps(_sample())) == []


def test_apply_params_substitutes_placeholder():
    rec = fmt.apply_params(_sample(), {"post_text": "Hallo Welt"})
    assert rec.steps[1].text == "Hallo Welt"
    # Original bleibt unangetastet (kein In-Place-Mutieren):
    original = _sample()
    fmt.apply_params(original, {"post_text": "Hallo Welt"})
    assert original.steps[1].text == "${post_text}"


def test_apply_params_uses_declared_default_and_allows_override():
    rec = _sample()
    rec.params[0]["default"] = "Standard"
    assert fmt.apply_params(rec, {}).steps[1].text == "Standard"
    assert fmt.apply_params(rec, {"post_text": "Explizit"}).steps[1].text == "Explizit"


def test_required_param_roundtrip_does_not_acquire_empty_default():
    rec = _sample()
    rec.params[0].pop("default")
    back = fmt.loads(fmt.dumps(rec))
    assert "default" not in back.params[0]
