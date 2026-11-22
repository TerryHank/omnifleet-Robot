from pathlib import Path


def test_foxglove_is_an_optional_health_gate():
    source = (Path(__file__).parents[1] / "omnifleet_localization" / "node.py").read_text(
        encoding="utf-8"
    )
    assert 'self.declare_parameter("require_foxglove", False)' in source
    assert "if self.require_foxglove and" in source
