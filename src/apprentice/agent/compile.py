"""Compile a SkillSpec with Nemotron on Token Factory."""

from __future__ import annotations

from apprentice.agent.client import TokenFactoryClient
from apprentice.config import Settings, load_settings
from apprentice.skill.prompts import COMPILE_SYSTEM, compile_user_prompt
from apprentice.skill.schema import SkillSpec, parse_skill_json


def compile_skill(
    description: str,
    *,
    settings: Settings | None = None,
    client: TokenFactoryClient | None = None,
) -> SkillSpec:
    settings = settings or load_settings()
    tf = client or TokenFactoryClient(settings)
    raw = tf.text(
        settings.nemotron_compile_model,
        [
            {"role": "system", "content": COMPILE_SYSTEM},
            {"role": "user", "content": compile_user_prompt(description)},
        ],
        max_tokens=800,
        temperature=0.1,
    )
    return parse_skill_json(raw)
