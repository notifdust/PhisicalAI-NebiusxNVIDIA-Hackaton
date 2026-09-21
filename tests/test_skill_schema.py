from apprentice.skill.schema import SkillSpec, default_skill1, parse_skill_json


def test_default_skill1_is_valid() -> None:
    spec = default_skill1()
    assert spec.name == "clear_table_to_bin"
    assert spec.language_instruction == "put the block in the blue bowl"
    assert "object in target bowl" in spec.success


def test_parse_fenced_json() -> None:
    raw = """Sure, here is the card:
```json
{
  "name": "Clear Table To Bin",
  "goal": "Place the block in the blue bowl",
  "language_instruction": "put the block in the blue bowl",
  "constraints": ["slow near the bowl"],
  "success": ["object in target bowl"],
  "recovery": ["retry grasp once", "stop and ask"]
}
```
"""
    spec = parse_skill_json(raw)
    assert spec.name == "clear_table_to_bin"
    assert spec.success == ["object in target bowl"]


def test_rejects_empty_success() -> None:
    try:
        SkillSpec(name="x", goal="do it", success=[])
    except Exception as exc:
        assert "success" in str(exc).lower()
    else:
        raise AssertionError("expected validation error")
