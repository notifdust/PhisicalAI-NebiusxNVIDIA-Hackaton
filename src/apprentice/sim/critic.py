"""Geometric critic from sim state. Cosmos Reasoner wraps this when a key exists."""

from __future__ import annotations

from apprentice.sim.env import TabletopSim
from apprentice.skill.schema import CriticVerdict, SkillSpec


def geometric_verdict(env: TabletopSim, skill: SkillSpec | None = None) -> CriticVerdict:
    success = env.success()
    mode = env.geometric_failure_mode()
    block = env.state.block
    bowl = env.state.bowl
    obs = (
        f"block=({block[0]:.3f},{block[1]:.3f},{block[2]:.3f}) "
        f"bowl=({bowl[0]:.3f},{bowl[1]:.3f}) gripped={env.state.gripped} "
        f"in_bowl={success}"
    )
    next_subgoal = None if success else ("retry grasp once" if mode == "grasp_missed" else "stop")
    return CriticVerdict(
        success=success,
        failure_mode=mode,
        next_subgoal=next_subgoal,
        observation=obs,
    )
