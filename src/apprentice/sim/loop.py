"""Closed sim loop: skill card → expert rollout → geometric (and optional Cosmos) critic."""

from __future__ import annotations

import json
from pathlib import Path

from apprentice.sim.critic import geometric_verdict
from apprentice.sim.env import TabletopSim
from apprentice.sim.expert import rollout
from apprentice.sim.record import record_episode
from apprentice.skill.schema import default_skill1


def run_loop(
    *,
    episodes: int = 5,
    dest: Path,
    start_seed: int = 0,
    miss_every: int = 0,
    use_cosmos: bool = False,
) -> dict:
    dest.mkdir(parents=True, exist_ok=True)
    skill = default_skill1()
    rows = []
    for i in range(episodes):
        seed = start_seed + i
        miss = miss_every > 0 and (i + 1) % miss_every == 0
        ep_dir = dest / f"episode_{i:03d}"
        payload = record_episode(ep_dir, seed=seed, miss=miss, save_images=True)
        env = TabletopSim(seed=seed)
        rollout(env, miss=miss)
        geo = geometric_verdict(env, skill)
        cosmos_text = None
        if use_cosmos:
            from apprentice.critic.reasoner import describe_scene

            frames = sorted((ep_dir / "frames").glob("front_*.jpg"))
            cosmos_text = describe_scene(frames[-1]) if frames else None
        rows.append(
            {
                "episode": i,
                "seed": seed,
                "success": payload["success"],
                "geometric": geo.model_dump(),
                "cosmos": cosmos_text,
                "path": str(ep_dir),
            }
        )
    n_ok = sum(1 for r in rows if r["success"])
    report = {
        "skill": skill.model_dump(),
        "episodes": episodes,
        "successes": n_ok,
        "success_rate": n_ok / episodes if episodes else 0.0,
        "rows": rows,
    }
    (dest / "report.json").write_text(json.dumps(report, indent=2) + "\n")
    return report
