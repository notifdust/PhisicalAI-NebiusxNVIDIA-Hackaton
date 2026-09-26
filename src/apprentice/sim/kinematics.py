"""Approximate SO-101 kinematics for the CPU tabletop simulator.

This is a development stand-in, not Isaac Lab. Joint names match LeRobot/GR00T.
Units: joint commands in degrees (gripper 0=closed, 100=open). Positions in metres.
"""

from __future__ import annotations

import math
from dataclasses import dataclass

import numpy as np

from apprentice.robot.so101 import JOINT_ORDER

# Link lengths (metres), close to community SO-101 numbers.
ZS = 0.055
L_UPPER = 0.130
L_FORE = 0.150
L_WRIST = 0.080  # wrist pitch origin to fingertips

JOINT_LIMITS_DEG: dict[str, tuple[float, float]] = {
    "shoulder_pan": (-110.0, 110.0),
    "shoulder_lift": (-20.0, 100.0),
    "elbow_flex": (-120.0, 0.0),
    "wrist_flex": (-130.0, 100.0),
    "wrist_roll": (-90.0, 90.0),
    "gripper": (0.0, 100.0),
}


@dataclass(frozen=True)
class ArmPose:
    joints: dict[str, float]
    shoulder: tuple[float, float, float]
    elbow: tuple[float, float, float]
    wrist: tuple[float, float, float]
    ee: tuple[float, float, float]


def _clip_joint(name: str, value: float) -> float:
    lo, hi = JOINT_LIMITS_DEG[name]
    return float(min(hi, max(lo, value)))


def normalize_joints(joints: dict[str, float]) -> dict[str, float]:
    out = {name: 0.0 for name in JOINT_ORDER}
    out.update(joints)
    return {name: _clip_joint(name, out[name]) for name in JOINT_ORDER}


def fk(joints: dict[str, float]) -> ArmPose:
    j = normalize_joints(joints)
    pan = math.radians(j["shoulder_pan"])
    lift = math.radians(j["shoulder_lift"])
    elbow = math.radians(j["elbow_flex"])
    wrist = math.radians(j["wrist_flex"])

    c, s = math.cos(pan), math.sin(pan)
    shoulder = (0.0, 0.0, ZS)

    def plane_to_world(r: float, z: float) -> tuple[float, float, float]:
        return (r * c, r * s, z)

    # lift=0: upper arm along +r (horizontal). Positive lift raises toward +z.
    r1 = L_UPPER * math.cos(lift)
    z1 = ZS + L_UPPER * math.sin(lift)
    elbow_xyz = plane_to_world(r1, z1)

    a2 = lift + elbow
    r2 = r1 + L_FORE * math.cos(a2)
    z2 = z1 + L_FORE * math.sin(a2)
    wrist_xyz = plane_to_world(r2, z2)

    a3 = a2 + wrist
    r3 = r2 + L_WRIST * math.cos(a3)
    z3 = z2 + L_WRIST * math.sin(a3)
    ee = plane_to_world(r3, z3)
    return ArmPose(joints=j, shoulder=shoulder, elbow=elbow_xyz, wrist=wrist_xyz, ee=ee)


def ik_xyz(x: float, y: float, z: float, *, gripper: float = 50.0) -> dict[str, float]:
    """IK with gripper pointing down (approach from above)."""
    pan = math.degrees(math.atan2(y, x))
    r = math.hypot(x, y)
    # Wrist is L_WRIST above the fingertips when the tool points -z.
    wr, wz = r, z + L_WRIST
    dz = wz - ZS
    reach = math.hypot(wr, dz)
    max_reach = L_UPPER + L_FORE - 1e-4
    if reach > max_reach:
        scale = max_reach / reach
        wr, dz = wr * scale, dz * scale
        reach = max_reach
    reach = max(reach, 1e-4)

    c2 = (wr**2 + dz**2 - L_UPPER**2 - L_FORE**2) / (2 * L_UPPER * L_FORE)
    c2 = float(np.clip(c2, -1.0, 1.0))
    s2 = -math.sqrt(max(0.0, 1.0 - c2 * c2))  # elbow folds negative
    elbow_deg = math.degrees(math.atan2(s2, c2))
    lift_deg = math.degrees(
        math.atan2(dz, wr) - math.atan2(L_FORE * s2, L_UPPER + L_FORE * c2)
    )

    # Tool angle in the plane = lift + elbow + wrist. Point gripper down (-90 deg).
    wrist_deg = -90.0 - lift_deg - elbow_deg
    return normalize_joints(
        {
            "shoulder_pan": pan,
            "shoulder_lift": lift_deg,
            "elbow_flex": elbow_deg,
            "wrist_flex": wrist_deg,
            "wrist_roll": 0.0,
            "gripper": gripper,
        }
    )


def lerp_joints(a: dict[str, float], b: dict[str, float], t: float) -> dict[str, float]:
    t = min(1.0, max(0.0, t))
    a = normalize_joints(a)
    b = normalize_joints(b)
    return {name: a[name] + (b[name] - a[name]) * t for name in JOINT_ORDER}
