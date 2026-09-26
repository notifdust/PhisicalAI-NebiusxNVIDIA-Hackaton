"""Cosmos 3 Super Reasoner: physical critic on Token Factory."""

from __future__ import annotations

import base64
import json
import re
from pathlib import Path

from apprentice.agent.client import TokenFactoryClient
from apprentice.config import Settings, load_settings
from apprentice.skill.schema import CriticVerdict, SkillSpec

REASONER_SYSTEM = """You are NVIDIA Cosmos 3 Super Reasoner acting as the physical critic
for a SO-101 tabletop arm. Look at camera frames and decide if the current subgoal succeeded.

Return ONLY JSON:
{
  "success": true,
  "failure_mode": null,
  "next_subgoal": null,
  "observation": "one sentence of what you see"
}

If success is false, set failure_mode to a short tag such as
"grasp_missed", "object_not_visible", "wrong_bowl", "collision", "timeout".
Set next_subgoal to what the arm should try next, or "stop" if a human must intervene.
"""


def image_to_data_url(path: Path) -> str:
    data = path.read_bytes()
    suffix = path.suffix.lower().lstrip(".")
    mime = {"jpg": "jpeg", "jpeg": "jpeg", "png": "png", "webp": "webp"}.get(suffix, "jpeg")
    b64 = base64.b64encode(data).decode("ascii")
    return f"data:image/{mime};base64,{b64}"


def describe_scene(
    image_path: Path,
    prompt: str = "What objects, bowls, and robot parts are visible? Be concrete.",
    *,
    settings: Settings | None = None,
    client: TokenFactoryClient | None = None,
) -> str:
    settings = settings or load_settings()
    tf = client or TokenFactoryClient(settings)
    url = image_to_data_url(image_path)
    return tf.text(
        settings.cosmos_reasoner_model,
        [
            {
                "role": "system",
                "content": "You are a physical AI reasoner. Describe the tabletop scene for a robot.",
            },
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": prompt},
                    {"type": "image_url", "image_url": {"url": url}},
                ],
            },
        ],
        max_tokens=512,
        temperature=0.0,
    )


def critique_skill(
    image_paths: list[Path],
    skill: SkillSpec,
    *,
    settings: Settings | None = None,
    client: TokenFactoryClient | None = None,
) -> CriticVerdict:
    settings = settings or load_settings()
    tf = client or TokenFactoryClient(settings)
    content: list[dict] = [
        {
            "type": "text",
            "text": (
                f"Skill: {skill.name}\nGoal: {skill.goal}\n"
                f"Success checks: {skill.success}\n"
                "Did this scene satisfy the success checks?"
            ),
        }
    ]
    for path in image_paths:
        content.append({"type": "image_url", "image_url": {"url": image_to_data_url(path)}})
    raw = tf.text(
        settings.cosmos_reasoner_model,
        [
            {"role": "system", "content": REASONER_SYSTEM},
            {"role": "user", "content": content},
        ],
        max_tokens=400,
        temperature=0.0,
    )
    text = raw.strip()
    fenced = re.search(r"```(?:json)?\s*(\{.*\})\s*```", text, re.DOTALL)
    if fenced:
        text = fenced.group(1)
    else:
        start, end = text.find("{"), text.rfind("}")
        if start != -1 and end > start:
            text = text[start : end + 1]
    return CriticVerdict.model_validate(json.loads(text))
