from types import SimpleNamespace

from apprentice.agent.client import TokenFactoryClient
from apprentice.agent.compile import compile_skill
from apprentice.config import Settings
from apprentice.critic.reasoner import critique_skill, describe_scene
from apprentice.skill.schema import default_skill1


class FakeCompletions:
    def __init__(self, content: str) -> None:
        self.content = content

    def create(self, **kwargs):  # noqa: ANN003
        message = SimpleNamespace(content=self.content)
        choice = SimpleNamespace(message=message)
        return SimpleNamespace(choices=[choice], model=kwargs["model"])


class FakeOpenAI:
    def __init__(self, content: str) -> None:
        self.chat = SimpleNamespace(completions=FakeCompletions(content))


def test_compile_skill_strips_markdown() -> None:
    settings = Settings(nebius_api_key="test")
    raw = """```json
{"name": "clear_table_to_bin", "goal": "bin the block",
 "language_instruction": "put the block in the blue bowl",
 "success": ["object in target bowl"], "recovery": ["stop and ask"]}
```"""
    client = TokenFactoryClient(settings, client=FakeOpenAI(raw))
    spec = compile_skill("pick block into blue bowl", settings=settings, client=client)
    assert spec.name == "clear_table_to_bin"
    assert spec.goal == "bin the block"


def test_describe_scene_uses_reasoner_model(tmp_path) -> None:
    from apprentice.critic.synthetic_table import write_synthetic_table

    image = write_synthetic_table(tmp_path / "table.jpg")
    settings = Settings(nebius_api_key="test")
    client = TokenFactoryClient(settings, client=FakeOpenAI("A red block sits left of a blue bowl."))
    text = describe_scene(image, settings=settings, client=client)
    assert "blue bowl" in text


def test_critique_skill_parses_verdict(tmp_path) -> None:
    from apprentice.critic.synthetic_table import write_synthetic_table

    image = write_synthetic_table(tmp_path / "table.jpg")
    settings = Settings(nebius_api_key="test")
    payload = '{"success": false, "failure_mode": "grasp_missed", "next_subgoal": "retry grasp once", "observation": "block still on table"}'
    client = TokenFactoryClient(settings, client=FakeOpenAI(payload))
    verdict = critique_skill([image], default_skill1(), settings=settings, client=client)
    assert verdict.success is False
    assert verdict.failure_mode == "grasp_missed"
