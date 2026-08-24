from pathlib import Path

ROOT = Path(__file__).parents[1]


def test_action_is_composite_and_uses_argument_array() -> None:
    action = (ROOT / "action.yml").read_text(encoding="utf-8")
    assert "using: composite" in action
    assert 'args=(--base "$ALTRECHECK_BASE"' in action
    assert 'python -m altrecheck "${args[@]}"' in action
    assert "eval " not in action


def test_mit_license_is_present() -> None:
    license_text = (ROOT / "LICENSE").read_text(encoding="utf-8")
    assert license_text.startswith("MIT License")
