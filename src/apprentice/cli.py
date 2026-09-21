"""Apprentice CLI: Token Factory hello-world and SO-101 bring-up."""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path

from apprentice.config import load_settings
from apprentice.robot.so101 import (
    MOTOR_IDS,
    SETUP_MOTOR_ORDER,
    calibrate_cmd,
    find_port_cmd,
    format_cmd,
    record_cmd,
    setup_motors_cmd,
    teleop_cmd,
)
from apprentice.robot.waypoints import (
    WAYPOINTS_PATH,
    assert_captured,
    example_program,
    interpolate,
    load_program,
)
from apprentice.skill.schema import default_skill1


def _run(argv: list[str], *, dry: bool) -> int:
    print(format_cmd(argv))
    if dry:
        return 0
    return subprocess.call(argv)


def cmd_hello_nemotron(_: argparse.Namespace) -> int:
    from apprentice.agent.client import TokenFactoryClient

    settings = load_settings()
    tf = TokenFactoryClient(settings)
    text = tf.text(
        settings.nemotron_fast_model,
        [
            {
                "role": "system",
                "content": "You are the Apprentice agent runtime. Answer in one short sentence.",
            },
            {
                "role": "user",
                "content": "Name the first tabletop skill we are teaching the SO-101.",
            },
        ],
        max_tokens=128,
    )
    print(text.strip())
    print(f"\nmodel={settings.nemotron_fast_model}")
    print(f"base_url={settings.nebius_base_url}")
    return 0


def cmd_hello_reasoner(args: argparse.Namespace) -> int:
    from apprentice.critic.reasoner import describe_scene
    from apprentice.critic.synthetic_table import write_synthetic_table

    image = Path(args.image) if args.image else write_synthetic_table()
    text = describe_scene(image)
    print(text.strip())
    print(f"\nimage={image}")
    print(f"model={load_settings().cosmos_reasoner_model}")
    return 0


def cmd_compile_skill(args: argparse.Namespace) -> int:
    from apprentice.agent.compile import compile_skill

    description = args.text
    if args.file:
        description = Path(args.file).read_text()
    if not description:
        description = (
            "Teleop demo: pick a colored block from the table and place it in the blue bowl. "
            "Wrist and front cameras. One retry if the grasp misses."
        )
    spec = compile_skill(description)
    print(spec.model_dump_json(indent=2))
    return 0


def cmd_skill_default(_: argparse.Namespace) -> int:
    print(default_skill1().model_dump_json(indent=2))
    return 0


def cmd_robot_ids(_: argparse.Namespace) -> int:
    print("Set IDs ONE MOTOR AT A TIME, in this order (LeRobot default):\n")
    for name in SETUP_MOTOR_ORDER:
        print(f"  {name:16}  id={MOTOR_IDS[name]}")
    print("\nNever daisy-chain until every motor has a unique id.")
    return 0


def cmd_robot_find_port(args: argparse.Namespace) -> int:
    return _run(find_port_cmd(), dry=args.dry_run)


def cmd_robot_setup(args: argparse.Namespace) -> int:
    return _run(setup_motors_cmd(args.arm), dry=args.dry_run)


def cmd_robot_calibrate(args: argparse.Namespace) -> int:
    return _run(calibrate_cmd(args.arm), dry=args.dry_run)


def cmd_robot_teleop(args: argparse.Namespace) -> int:
    return _run(teleop_cmd(), dry=args.dry_run)


def cmd_robot_record(args: argparse.Namespace) -> int:
    return _run(record_cmd(num_episodes=args.episodes), dry=args.dry_run)


def cmd_robot_print(args: argparse.Namespace) -> int:
    print("# 1. find serial ports")
    print(format_cmd(find_port_cmd()))
    print("\n# 2. set motor IDs (one motor connected at a time)")
    print(format_cmd(setup_motors_cmd("follower")))
    print(format_cmd(setup_motors_cmd("leader")))
    print("\n# 3. calibrate (joints mid-range, then sweep each joint)")
    print(format_cmd(calibrate_cmd("follower")))
    print(format_cmd(calibrate_cmd("leader")))
    print("\n# 4. teleop")
    print(format_cmd(teleop_cmd()))
    print("\n# 5. record Skill 1 (minimum 5 episodes)")
    print(format_cmd(record_cmd(num_episodes=5)))
    return 0


def cmd_robot_cameras(_: argparse.Namespace) -> int:
    try:
        import cv2  # type: ignore
    except ImportError:
        print("OpenCV is not installed. pip install opencv-python, then rerun.", file=sys.stderr)
        return 1
    print("Probing indices 0–9. Use the two that show front table and wrist.\n")
    for idx in range(10):
        cap = cv2.VideoCapture(idx)
        ok = cap.isOpened()
        if ok:
            w = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
            h = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
            print(f"  index {idx}: open  {w}x{h}")
        cap.release()
    return 0


def cmd_robot_example_waypoints(_: argparse.Namespace) -> int:
    settings = load_settings()
    program = example_program(settings.skill1_instruction)
    dest = Path("configs/skill1_waypoints.example.json")
    dest.parent.mkdir(parents=True, exist_ok=True)
    dest.write_text(program.model_dump_json(indent=2) + "\n")
    print(f"wrote {dest} (all zeros — capture real poses before replay)")
    return 0


def cmd_robot_replay(args: argparse.Namespace) -> int:
    path = Path(args.waypoints) if args.waypoints else WAYPOINTS_PATH
    program = load_program(path)
    assert_captured(program)
    frames = interpolate(program)
    print(f"instruction={program.instruction}")
    print(f"waypoints={len(program.waypoints)} frames={len(frames)} fps={program.fps}")
    if args.dry_run:
        print("dry-run: not sending to the arm")
        return 0
    try:
        from apprentice.robot.lerobot_io import follower_types

        SO101Follower, SO101FollowerConfig = follower_types()
    except ImportError:
        print(
            "lerobot is not installed. Install extras: pip install -e '.[robot]'\n"
            "Then replay on the machine that has the SO-101 plugged in.",
            file=sys.stderr,
        )
        return 1
    settings = load_settings()
    robot = SO101Follower(
        SO101FollowerConfig(port=settings.so101_follower_port, id=settings.so101_follower_id)
    )
    robot.connect()
    try:
        period = 1.0 / max(program.fps, 1)
        import time

        for action in frames:
            robot.send_action(action)
            time.sleep(period)
    finally:
        robot.disconnect()
    return 0


def cmd_robot_capture_pose(args: argparse.Namespace) -> int:
    """Read current follower joints and print a waypoint JSON snippet."""
    try:
        from apprentice.robot.lerobot_io import follower_types

        SO101Follower, SO101FollowerConfig = follower_types()
    except ImportError:
        print("lerobot is not installed. pip install -e '.[robot]'", file=sys.stderr)
        return 1
    settings = load_settings()
    robot = SO101Follower(
        SO101FollowerConfig(port=settings.so101_follower_port, id=settings.so101_follower_id)
    )
    robot.connect()
    try:
        obs = robot.get_observation()
        joints = {}
        gripper = None
        for key, value in obs.items():
            if not key.endswith(".pos"):
                continue
            name = key.removesuffix(".pos")
            if name == "gripper":
                gripper = float(value)
            else:
                joints[name] = float(value)
        waypoint = {
            "name": args.name,
            "hold_s": args.hold,
            "gripper": gripper,
            "joints": joints,
        }
        print(json.dumps(waypoint, indent=2))
    finally:
        robot.disconnect()
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="apprentice", description=__doc__)
    sub = parser.add_subparsers(dest="command", required=True)

    sub.add_parser("hello-nemotron", help="Token Factory Nemotron ping").set_defaults(
        func=cmd_hello_nemotron
    )
    reasoner = sub.add_parser("hello-reasoner", help="Token Factory Cosmos Reasoner on an image")
    reasoner.add_argument("--image", help="JPEG/PNG path (synthetic table if omitted)")
    reasoner.set_defaults(func=cmd_hello_reasoner)

    compile_p = sub.add_parser("compile-skill", help="Nemotron drafts a SkillSpec JSON card")
    compile_p.add_argument("--text", default="", help="demonstration notes")
    compile_p.add_argument("--file", help="read demonstration notes from a file")
    compile_p.set_defaults(func=cmd_compile_skill)

    sub.add_parser("skill-default", help="print the locked Skill 1 card").set_defaults(
        func=cmd_skill_default
    )

    robot = sub.add_parser("robot", help="SO-101 bring-up")
    rsub = robot.add_subparsers(dest="robot_command", required=True)

    def _dry(p: argparse.ArgumentParser) -> None:
        p.add_argument("--dry-run", action="store_true", help="print the LeRobot command only")

    rsub.add_parser("ids", help="print motor ID assignment order").set_defaults(func=cmd_robot_ids)

    p = rsub.add_parser("find-port", help="identify USB motor-bus ports")
    _dry(p)
    p.set_defaults(func=cmd_robot_find_port)

    p = rsub.add_parser("setup-motors", help="set unique IDs (ONE motor plugged in at a time)")
    p.add_argument("--arm", choices=("follower", "leader"), required=True)
    _dry(p)
    p.set_defaults(func=cmd_robot_setup)

    p = rsub.add_parser("calibrate", help="calibrate an arm")
    p.add_argument("--arm", choices=("follower", "leader"), required=True)
    _dry(p)
    p.set_defaults(func=cmd_robot_calibrate)

    p = rsub.add_parser("teleop", help="leader drives follower")
    _dry(p)
    p.set_defaults(func=cmd_robot_teleop)

    p = rsub.add_parser("record", help="record Skill 1 episodes")
    p.add_argument("--episodes", type=int, default=5)
    _dry(p)
    p.set_defaults(func=cmd_robot_record)

    rsub.add_parser("print", help="print the full bring-up command list").set_defaults(
        func=cmd_robot_print
    )
    rsub.add_parser("cameras", help="probe OpenCV camera indices").set_defaults(
        func=cmd_robot_cameras
    )
    rsub.add_parser("example-waypoints", help="write placeholder Skill 1 waypoint file").set_defaults(
        func=cmd_robot_example_waypoints
    )

    p = rsub.add_parser("capture-pose", help="print current follower joints as a waypoint")
    p.add_argument("--name", default="pose")
    p.add_argument("--hold", type=float, default=0.8)
    p.set_defaults(func=cmd_robot_capture_pose)

    p = rsub.add_parser("replay", help="scripted waypoint replay (refuses all-zero placeholders)")
    p.add_argument("--waypoints", help="path to skill1_waypoints.json")
    _dry(p)
    p.set_defaults(func=cmd_robot_replay)

    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    try:
        return int(args.func(args))
    except KeyboardInterrupt:
        return 130
    except Exception as exc:  # noqa: BLE001 — CLI boundary
        print(f"error: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
