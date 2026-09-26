from pathlib import Path

import numpy as np

from apprentice.cli import main
from apprentice.sim.critic import geometric_verdict
from apprentice.sim.env import TabletopSim
from apprentice.sim.expert import rollout
from apprentice.sim.kinematics import fk, ik_xyz
from apprentice.sim.loop import run_loop
from apprentice.sim.record import evaluate, record_episode
from apprentice.skill.schema import default_skill1


def test_ik_reaches_overhead_point() -> None:
    joints = ik_xyz(0.24, 0.04, 0.04, gripper=70.0)
    pose = fk(joints)
    err = np.linalg.norm(np.array(pose.ee) - np.array([0.24, 0.04, 0.04]))
    assert err < 0.02


def test_expert_succeeds_on_fixed_seed() -> None:
    env = TabletopSim(seed=0)
    rollout(env)
    assert env.success()
    verdict = geometric_verdict(env, default_skill1())
    assert verdict.success is True
    assert verdict.failure_mode is None


def test_injected_miss_fails_and_is_tagged() -> None:
    env = TabletopSim(seed=1)
    rollout(env, miss=True)
    assert env.success() is False
    assert env.geometric_failure_mode() == "grasp_missed"


def test_evaluate_high_success_rate() -> None:
    summary = evaluate(episodes=8, start_seed=0, miss_every=0)
    assert summary["success_rate"] >= 0.875


def test_record_writes_images_and_json(tmp_path: Path) -> None:
    payload = record_episode(tmp_path / "ep", seed=2, save_images=True)
    assert payload["success"] is True
    assert (tmp_path / "ep" / "episode.json").exists()
    fronts = list((tmp_path / "ep" / "frames").glob("front_*.jpg"))
    wrists = list((tmp_path / "ep" / "frames").glob("wrist_*.jpg"))
    assert fronts and wrists


def test_closed_loop_report(tmp_path: Path) -> None:
    report = run_loop(episodes=3, dest=tmp_path / "loop", start_seed=0)
    assert report["skill"]["name"] == "clear_table_to_bin"
    assert report["success_rate"] == 1.0
    assert (tmp_path / "loop" / "report.json").exists()


def test_cli_sim_eval(tmp_path: Path) -> None:
    out = tmp_path / "eval.json"
    assert main(["sim", "eval", "--episodes", "4", "--out", str(out), "--min-rate", "0.75"]) == 0
    assert out.exists()
