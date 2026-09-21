"""Scripted Skill 1 baseline: replay captured joint waypoints. Not a learned policy."""

from __future__ import annotations

from pathlib import Path

from pydantic import BaseModel, Field, field_validator

from apprentice.robot.so101 import JOINT_ORDER, repo_root

WAYPOINTS_PATH = repo_root() / "configs" / "skill1_waypoints.json"


class Waypoint(BaseModel):
    name: str
    hold_s: float = Field(default=0.8, ge=0.0, le=10.0)
    gripper: float | None = Field(default=None, ge=0.0, le=100.0)
    joints: dict[str, float]

    @field_validator("joints")
    @classmethod
    def known_joints(cls, value: dict[str, float]) -> dict[str, float]:
        extra = set(value) - set(JOINT_ORDER)
        if extra:
            raise ValueError(f"unknown joints: {sorted(extra)}")
        return value


class WaypointProgram(BaseModel):
    instruction: str
    fps: int = 30
    waypoints: list[Waypoint]


def load_program(path: Path | None = None) -> WaypointProgram:
    target = path or WAYPOINTS_PATH
    if not target.exists():
        raise FileNotFoundError(
            f"{target} is missing. Copy configs/skill1_waypoints.example.json "
            "and capture real joints on metal with: apprentice robot capture-pose"
        )
    return WaypointProgram.model_validate_json(target.read_text())


def assert_captured(program: WaypointProgram) -> None:
    """Refuse to command the arm with the placeholder all-zero example."""
    if not program.waypoints:
        raise ValueError("no waypoints")
    if all(all(v == 0.0 for v in wp.joints.values()) for wp in program.waypoints):
        raise ValueError(
            "waypoints are still the all-zero example. "
            "Capture poses on the real SO-101 before replay."
        )


def interpolate(program: WaypointProgram) -> list[dict[str, float]]:
    """Expand holds into a flat action stream at program.fps (joint dicts)."""
    frames: list[dict[str, float]] = []
    for wp in program.waypoints:
        action = {f"{name}.pos": wp.joints.get(name, 0.0) for name in JOINT_ORDER}
        if wp.gripper is not None:
            action["gripper.pos"] = wp.gripper
        n = max(1, int(wp.hold_s * program.fps))
        frames.extend(action for _ in range(n))
    return frames


def dump_program(program: WaypointProgram, path: Path | None = None) -> Path:
    target = path or WAYPOINTS_PATH
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(program.model_dump_json(indent=2) + "\n")
    return target


def example_program(instruction: str) -> WaypointProgram:
    zeros = {name: 0.0 for name in JOINT_ORDER}
    return WaypointProgram(
        instruction=instruction,
        waypoints=[
            Waypoint(name="home", hold_s=1.0, gripper=50.0, joints=dict(zeros)),
            Waypoint(name="hover_object", hold_s=1.0, gripper=50.0, joints=dict(zeros)),
            Waypoint(name="grasp", hold_s=0.6, gripper=10.0, joints=dict(zeros)),
            Waypoint(name="hover_bowl", hold_s=1.0, gripper=10.0, joints=dict(zeros)),
            Waypoint(name="release", hold_s=0.6, gripper=80.0, joints=dict(zeros)),
            Waypoint(name="home", hold_s=1.0, gripper=50.0, joints=dict(zeros)),
        ],
    )
