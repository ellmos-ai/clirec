from clirec.config import merge_config, recorder_config_from_dict
from clirec.recorder import RecorderConfig


def test_config_has_clirec_defaults():
    cfg = merge_config()
    assert cfg["ringbuffer_enabled"] is False
    assert cfg["ringbuffer_minutes"] == 15
    assert cfg["recordings_dir"] == "recordings"


def test_config_loads_clirec_override_from_dict():
    cfg = merge_config({"ringbuffer_enabled": True, "ringbuffer_minutes": 30})
    assert cfg["ringbuffer_enabled"] is True
    assert cfg["ringbuffer_minutes"] == 30
    # untouched keys keep defaults
    assert cfg["recordings_dir"] == "recordings"


def test_clirec_recorder_config_mapping():
    rc = recorder_config_from_dict({"ringbuffer_enabled": True})
    assert isinstance(rc, RecorderConfig)
    assert rc.ringbuffer_enabled is True and rc.ringbuffer_minutes == 15
