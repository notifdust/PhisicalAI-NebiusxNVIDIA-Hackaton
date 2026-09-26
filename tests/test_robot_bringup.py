from pathlib import Path

import pytest

from apprentice.cli import main
from apprentice.robot.so101 import MOTOR_IDS, SETUP_MOTOR_ORDER, format_cmd, record_cmd, teleop_cmd
from apprentice.robot.waypoints import assert_captured, example_program, interpolate, load_program


def test_motor_setup_order_starts_at_gripper() -> None:
    assert SETUP_MOTOR_ORDER[0] == "gripper"
    assert SETUP_MOTOR_ORDER[-1] == "shoulder_pan"
    assert MOTOR_IDS["gripper"] == 6
    assert MOTOR_IDS["shoulder_pan"] == 1


def test_teleop_command_includes_canonical_skill_cameras() -> None:
    line = format_cmd(teleop_cmd())
    assert "so101_follower" in line
    assert "so101_leader" in line
    assert "front:" in line
    assert "wrist:" in line


def test_record_command_locks_skill1_language() -> None:
    argv = record_cmd(num_episodes=5)
    joined = " ".join(argv)
    assert "put the block in the blue bowl" in joined
    assert "num_episodes=5" in joined


def test_example_waypoints_refuse_replay() -> None:
    program = example_program("put the block in the blue bowl")
    with pytest.raises(ValueError, match="all-zero"):
        assert_captured(program)


def test_load_example_waypoints_and_interpolate() -> None:
    path = Path("configs/skill1_waypoints.example.json")
    program = load_program(path)
    frames = interpolate(program)
    assert len(frames) >= 30
    assert "shoulder_pan.pos" in frames[0]


def test_cli_print_is_dry() -> None:
    assert main(["skill-default"]) == 0
    assert main(["robot", "ids"]) == 0
    assert main(["robot", "print"]) == 0
    assert main(["robot", "teleop", "--dry-run"]) == 0


def test_cli_replay_refuses_example_waypoints() -> None:
    assert (
        main(
            [
                "robot",
                "replay",
                "--waypoints",
                "configs/skill1_waypoints.example.json",
                "--dry-run",
            ]
        )
        == 1
    )
