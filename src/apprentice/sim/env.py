"""CPU tabletop environment: 6-DOF arm, one block, one bowl, two cameras."""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np

from apprentice.sim.kinematics import fk, ik_xyz, normalize_joints
from apprentice.sim.render import render_views
from apprentice.skill.schema import SKILL1_DEFAULT_INSTRUCTION


@dataclass
class SimConfig:
    instruction: str = SKILL1_DEFAULT_INSTRUCTION
    fps: int = 20
    image_size: tuple[int, int] = (320, 240)
    bowl_radius: float = 0.045
    block_size: float = 0.028
    grasp_radius: float = 0.032
    table_z: float = 0.0


@dataclass
class SimState:
    joints: dict[str, float]
    block: np.ndarray
    bowl: np.ndarray
    gripped: bool = False
    light: float = 1.0
    block_rgb: tuple[int, int, int] = (200, 48, 48)
    bowl_rgb: tuple[int, int, int] = (40, 90, 190)


class TabletopSim:
    """Development body. Same skill and joint names as the real SO-101."""

    def __init__(self, config: SimConfig | None = None, seed: int | None = None) -> None:
        self.config = config or SimConfig()
        self.rng = np.random.default_rng(seed)
        self.state = self._spawn()
        self._images: dict[str, np.ndarray] = {}
        self._render()

    def _spawn(self) -> SimState:
        block_xy = np.array(
            [self.rng.uniform(0.16, 0.20), self.rng.uniform(-0.05, 0.05)], dtype=np.float64
        )
        bowl_xy = np.array(
            [self.rng.uniform(0.22, 0.26), self.rng.uniform(-0.05, 0.05)], dtype=np.float64
        )
        # Keep them apart so Skill 1 is an actual transfer, not a drop-in-place.
        if np.linalg.norm(block_xy - bowl_xy) < 0.055:
            bowl_xy[1] = -0.05 if bowl_xy[1] >= 0 else 0.05
        home = ik_xyz(0.18, 0.0, 0.16, gripper=70.0)
        light = float(self.rng.uniform(0.75, 1.15))
        jitter = int(self.rng.integers(-25, 26))
        block_rgb = (int(np.clip(200 + jitter, 120, 255)), 40, 40)
        return SimState(
            joints=home,
            block=np.array([block_xy[0], block_xy[1], self.config.block_size / 2], dtype=np.float64),
            bowl=np.array([bowl_xy[0], bowl_xy[1], 0.0], dtype=np.float64),
            gripped=False,
            light=light,
            block_rgb=block_rgb,
        )

    def reset(self, seed: int | None = None) -> dict:
        if seed is not None:
            self.rng = np.random.default_rng(seed)
        self.state = self._spawn()
        self._render()
        return self.observation()

    def _render(self) -> None:
        pose = fk(self.state.joints)
        self._images = render_views(
            pose,
            block=tuple(self.state.block.tolist()),
            bowl=tuple(self.state.bowl.tolist()),
            bowl_radius=self.config.bowl_radius,
            block_size=self.config.block_size,
            gripped=self.state.gripped,
            light=self.state.light,
            width=self.config.image_size[0],
            height=self.config.image_size[1],
            block_rgb=self.state.block_rgb,
            bowl_rgb=self.state.bowl_rgb,
        )

    def _apply_grasp(self, prev_gripper: float, new_gripper: float) -> None:
        pose = fk(self.state.joints)
        ee = np.array(pose.ee)
        dist = float(np.linalg.norm(ee - self.state.block))
        closing = prev_gripper > 45.0 and new_gripper < 35.0
        opening = prev_gripper < 40.0 and new_gripper > 55.0
        if closing and dist <= self.config.grasp_radius and ee[2] < self.state.block[2] + 0.04:
            self.state.gripped = True
        if opening and self.state.gripped:
            self.state.gripped = False
            self.state.block[2] = self.config.block_size / 2

    def step(self, action: dict[str, float]) -> dict:
        prev_g = self.state.joints["gripper"]
        self.state.joints = normalize_joints({**self.state.joints, **action})
        self._apply_grasp(prev_g, self.state.joints["gripper"])
        if self.state.gripped:
            self.state.block = np.array(fk(self.state.joints).ee, dtype=np.float64)
        else:
            self.state.block[2] = self.config.block_size / 2
        self._render()
        return self.observation()

    def success(self) -> bool:
        if self.state.gripped:
            return False
        xy = np.linalg.norm(self.state.block[:2] - self.state.bowl[:2])
        return bool(xy <= self.config.bowl_radius * 0.85)

    def observation(self) -> dict:
        pose = fk(self.state.joints)
        return {
            "instruction": self.config.instruction,
            "joints": dict(self.state.joints),
            "action": dict(self.state.joints),
            "ee": pose.ee,
            "block": tuple(float(v) for v in self.state.block),
            "bowl": tuple(float(v) for v in self.state.bowl),
            "gripped": self.state.gripped,
            "success": self.success(),
            "images": self._images,
        }

    def geometric_failure_mode(self) -> str | None:
        if self.success():
            return None
        if self.state.gripped:
            return "still_held"
        xy = float(np.linalg.norm(self.state.block[:2] - self.state.bowl[:2]))
        if xy > self.config.bowl_radius:
            pose = fk(self.state.joints)
            dist_ee = float(np.linalg.norm(np.array(pose.ee) - self.state.block))
            if dist_ee > 0.06:
                return "grasp_missed"
            return "wrong_bowl"
        return "timeout"
