"""Skill card: the object that teach, factory, and run all pass around."""

from __future__ import annotations

import re
from typing import Any

from pydantic import BaseModel, Field, field_validator


SKILL1_NAME = "clear_table_to_bin"
SKILL1_DEFAULT_INSTRUCTION = "put the block in the blue bowl"


class SkillSources(BaseModel):
    demo_episode: str | None = None
    tavily: list[str] = Field(default_factory=list)


class SkillSpec(BaseModel):
    """Compiler output. Keep this schema stable — factory and runtime depend on it."""

    name: str = Field(min_length=1)
    goal: str = Field(min_length=1)
    language_instruction: str = Field(
        default=SKILL1_DEFAULT_INSTRUCTION,
        description="Canonical phrase stored on every LeRobot episode.",
    )
    constraints: list[str] = Field(default_factory=list)
    success: list[str] = Field(default_factory=list)
    recovery: list[str] = Field(default_factory=list)
    sources: SkillSources = Field(default_factory=SkillSources)

    @field_validator("name")
    @classmethod
    def slug_name(cls, value: str) -> str:
        slug = re.sub(r"[^a-z0-9_]+", "_", value.strip().lower()).strip("_")
        if not slug:
            raise ValueError("name must contain letters or digits")
        return slug

    @field_validator("success")
    @classmethod
    def success_not_empty(cls, value: list[str]) -> list[str]:
        if not value:
            raise ValueError("success must list at least one observable check")
        return value


class CriticVerdict(BaseModel):
    success: bool
    failure_mode: str | None = None
    next_subgoal: str | None = None
    observation: str = ""


def default_skill1() -> SkillSpec:
    return SkillSpec(
        name=SKILL1_NAME,
        goal="Place the visible object into the matching bowl",
        language_instruction=SKILL1_DEFAULT_INSTRUCTION,
        constraints=[
            "Keep the workspace clear of people during motion",
            "One retry then stop",
        ],
        success=[
            "object in target bowl",
            "gripper open",
            "arm clear of table",
        ],
        recovery=["re-detect", "retry grasp once", "stop and ask"],
    )


def parse_skill_json(payload: str | dict[str, Any]) -> SkillSpec:
    if isinstance(payload, dict):
        return SkillSpec.model_validate(payload)
    text = payload.strip()
    fenced = re.search(r"```(?:json)?\s*(\{.*\})\s*```", text, re.DOTALL)
    if fenced:
        text = fenced.group(1)
    else:
        start, end = text.find("{"), text.rfind("}")
        if start == -1 or end == -1 or end <= start:
            raise ValueError("no JSON object found in model output")
        text = text[start : end + 1]
    return SkillSpec.model_validate_json(text)
