"""Record and evaluate simulated Skill 1 episodes."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from apprentice.sim.env import TabletopSim
from apprentice.sim.expert import rollout
from apprentice.sim.render import save_jpeg
from apprentice.skill.schema import SKILL1_DEFAULT_INSTRUCTION, default_skill1
from apprentice.sim.critic import geometric_verdict


def _strip_images(obs: dict) -> dict[str, Any]:
    return {k: v for k, v in obs.items() if k != "images"}


def record_episode(
    dest: Path,
    *,
    seed: int,
    miss: bool = False,
    save_images: bool = True,
    key_frames_only: bool = True,
) -> dict[str, Any]:
    env = TabletopSim(seed=seed)
    frames = rollout(env, miss=miss)
    dest.mkdir(parents=True, exist_ok=True)
    payload = {
        "instruction": SKILL1_DEFAULT_INSTRUCTION,
        "backend": "tabletop_dev",
        "seed": seed,
        "miss": miss,
        "success": env.success(),
        "n_frames": len(frames),
        "fps": env.config.fps,
        "verdict": geometric_verdict(env, default_skill1()).model_dump(),
        "frames": [_strip_images(f) for f in frames],
    }
    (dest / "episode.json").write_text(json.dumps(payload, indent=2) + "\n")
    if save_images and frames:
        img_dir = dest / "frames"
        img_dir.mkdir(exist_ok=True)
        indices = [0, len(frames) // 2, len(frames) - 1] if key_frames_only else range(len(frames))
        for i in indices:
            for cam, arr in frames[i]["images"].items():
                save_jpeg(arr, img_dir / f"{cam}_{i:04d}.jpg")
    return payload


def evaluate(
    *,
    episodes: int,
    start_seed: int = 0,
    dest: Path | None = None,
    miss_every: int = 0,
) -> dict[str, Any]:
    results = []
    for i in range(episodes):
        seed = start_seed + i
        miss = miss_every > 0 and (i + 1) % miss_every == 0
        env = TabletopSim(seed=seed)
        rollout(env, miss=miss)
        ok = env.success()
        results.append(
            {
                "seed": seed,
                "success": ok,
                "miss_injected": miss,
                "failure_mode": env.geometric_failure_mode(),
            }
        )
    n_ok = sum(1 for r in results if r["success"])
    summary = {
        "backend": "tabletop_dev",
        "instruction": SKILL1_DEFAULT_INSTRUCTION,
        "episodes": episodes,
        "successes": n_ok,
        "success_rate": n_ok / episodes if episodes else 0.0,
        "results": results,
    }
    if dest is not None:
        dest.parent.mkdir(parents=True, exist_ok=True)
        dest.write_text(json.dumps(summary, indent=2) + "\n")
    return summary


def domain_random_eval(*, episodes: int, start_seed: int = 100, dest: Path | None = None) -> dict:
    """Factory stand-in: same expert, randomized layouts/lighting. Cosmos replaces this later."""
    return evaluate(episodes=episodes, start_seed=start_seed, dest=dest, miss_every=0)
