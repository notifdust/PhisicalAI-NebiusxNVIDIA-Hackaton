"""Scripted Skill 1 expert. Stand-in for GR00T until a policy is trained."""

from __future__ import annotations

from collections.abc import Iterator

from apprentice.sim.env import TabletopSim
from apprentice.sim.kinematics import ik_xyz, lerp_joints


def _hold(env: TabletopSim, joints: dict[str, float], steps: int) -> Iterator[dict]:
    for _ in range(max(1, steps)):
        yield env.step(joints)


def _move(env: TabletopSim, target: dict[str, float], steps: int) -> Iterator[dict]:
    start = dict(env.state.joints)
    steps = max(1, steps)
    for i in range(1, steps + 1):
        yield env.step(lerp_joints(start, target, i / steps))


def expert_actions(env: TabletopSim, *, miss: bool = False) -> Iterator[dict]:
    """Cartesian pick-and-place through IK. If miss=True, close too high on purpose."""
    block = env.state.block
    bowl = env.state.bowl
    g_open, g_close = 80.0, 12.0
    hover_z, grasp_z, carry_z = 0.13, 0.028, 0.15
    if miss:
        grasp_z = 0.09

    home = ik_xyz(0.18, 0.0, 0.16, gripper=g_open)
    above_block = ik_xyz(float(block[0]), float(block[1]), hover_z, gripper=g_open)
    at_block = ik_xyz(float(block[0]), float(block[1]), grasp_z, gripper=g_open)
    closed = {**at_block, "gripper": g_close}
    lift_block = ik_xyz(float(block[0]), float(block[1]), carry_z, gripper=g_close)
    above_bowl = ik_xyz(float(bowl[0]), float(bowl[1]), carry_z, gripper=g_close)
    at_bowl = ik_xyz(float(bowl[0]), float(bowl[1]), 0.04, gripper=g_close)
    open_bowl = {**at_bowl, "gripper": g_open}
    lift_empty = ik_xyz(float(bowl[0]), float(bowl[1]), 0.14, gripper=g_open)

    yield from _move(env, home, 6)
    yield from _move(env, above_block, 10)
    yield from _move(env, at_block, 8)
    yield from _hold(env, closed, 4)
    yield from _move(env, lift_block, 8)
    yield from _move(env, above_bowl, 12)
    yield from _move(env, at_bowl, 8)
    yield from _hold(env, open_bowl, 4)
    yield from _move(env, lift_empty, 8)
    yield from _move(env, home, 8)


def rollout(env: TabletopSim, *, miss: bool = False) -> list[dict]:
    frames = [env.observation()]
    for obs in expert_actions(env, miss=miss):
        frames.append(obs)
    return frames
