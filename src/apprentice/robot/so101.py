"""SO-101 constants, LeRobot command builders, waypoint replay."""

from __future__ import annotations

from pathlib import Path

from apprentice.config import Settings, load_settings

# Official LeRobot / GR00T embodiment map. IDs must match lerobot-setup-motors.
MOTOR_IDS: dict[str, int] = {
    "shoulder_pan": 1,
    "shoulder_lift": 2,
    "elbow_flex": 3,
    "wrist_flex": 4,
    "wrist_roll": 5,
    "gripper": 6,
}

JOINT_ORDER = tuple(MOTOR_IDS.keys())

# Follower: all STS3215 1/345. Leader mix is required for a light teleop arm.
FOLLOWER_GEAR = "1/345 STS3215 (all six joints)"
LEADER_GEAR = {
    "shoulder_pan": "1/191",
    "shoulder_lift": "1/345",
    "elbow_flex": "1/191",
    "wrist_flex": "1/147",
    "wrist_roll": "1/147",
    "gripper": "1/147",
}

SETUP_MOTOR_ORDER = (
    "gripper",
    "wrist_roll",
    "wrist_flex",
    "elbow_flex",
    "shoulder_lift",
    "shoulder_pan",
)


def cameras_cli(settings: Settings | None = None) -> str:
    s = settings or load_settings()
    return (
        "{ "
        f"front: {{type: opencv, index_or_path: {s.so101_front_cam}, "
        f"width: {s.so101_cam_width}, height: {s.so101_cam_height}, fps: {s.so101_cam_fps}}}, "
        f"wrist: {{type: opencv, index_or_path: {s.so101_wrist_cam}, "
        f"width: {s.so101_cam_width}, height: {s.so101_cam_height}, fps: {s.so101_cam_fps}}}"
        " }"
    )


def find_port_cmd() -> list[str]:
    return ["lerobot-find-port"]


def setup_motors_cmd(arm: str, settings: Settings | None = None) -> list[str]:
    s = settings or load_settings()
    if arm == "follower":
        return [
            "lerobot-setup-motors",
            "--robot.type=so101_follower",
            f"--robot.port={s.so101_follower_port}",
        ]
    if arm == "leader":
        return [
            "lerobot-setup-motors",
            "--teleop.type=so101_leader",
            f"--teleop.port={s.so101_leader_port}",
        ]
    raise ValueError("arm must be 'follower' or 'leader'")


def calibrate_cmd(arm: str, settings: Settings | None = None) -> list[str]:
    s = settings or load_settings()
    if arm == "follower":
        return [
            "lerobot-calibrate",
            "--robot.type=so101_follower",
            f"--robot.port={s.so101_follower_port}",
            f"--robot.id={s.so101_follower_id}",
        ]
    if arm == "leader":
        return [
            "lerobot-calibrate",
            "--teleop.type=so101_leader",
            f"--teleop.port={s.so101_leader_port}",
            f"--teleop.id={s.so101_leader_id}",
        ]
    raise ValueError("arm must be 'follower' or 'leader'")


def teleop_cmd(settings: Settings | None = None) -> list[str]:
    s = settings or load_settings()
    return [
        "lerobot-teleoperate",
        "--robot.type=so101_follower",
        f"--robot.port={s.so101_follower_port}",
        f"--robot.id={s.so101_follower_id}",
        f"--robot.cameras={cameras_cli(s)}",
        "--teleop.type=so101_leader",
        f"--teleop.port={s.so101_leader_port}",
        f"--teleop.id={s.so101_leader_id}",
        "--display_data=true",
    ]


def record_cmd(
    *,
    num_episodes: int = 5,
    repo_id: str | None = None,
    settings: Settings | None = None,
) -> list[str]:
    s = settings or load_settings()
    user = s.hf_user or "YOUR_HF_USER"
    repo = repo_id or f"{user}/apprentice-skill1"
    return [
        "lerobot-record",
        "--robot.type=so101_follower",
        f"--robot.port={s.so101_follower_port}",
        f"--robot.id={s.so101_follower_id}",
        f"--robot.cameras={cameras_cli(s)}",
        "--teleop.type=so101_leader",
        f"--teleop.port={s.so101_leader_port}",
        f"--teleop.id={s.so101_leader_id}",
        f"--dataset.repo_id={repo}",
        f"--dataset.num_episodes={num_episodes}",
        f"--dataset.single_task={s.skill1_instruction}",
        "--dataset.streaming_encoding=true",
        "--display_data=true",
    ]


def format_cmd(argv: list[str]) -> str:
    """Pretty-print a LeRobot argv for copy/paste."""
    out: list[str] = []
    for token in argv:
        if token.startswith("--robot.cameras="):
            key, value = token.split("=", 1)
            out.append(f'{key}="{value}"')
        elif token.startswith("--dataset.single_task="):
            key, value = token.split("=", 1)
            out.append(f'{key}="{value}"')
        else:
            out.append(token)
    return " \\\n    ".join(out)


def repo_root() -> Path:
    return Path(__file__).resolve().parents[3]
