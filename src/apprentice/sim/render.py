"""Orthographic front + wrist cameras for the CPU tabletop sim."""

from __future__ import annotations

import numpy as np
from PIL import Image, ImageDraw

from apprentice.sim.kinematics import ArmPose


def _px(x: float, z: float, *, origin_x: float, origin_z: float, scale: float, h: int) -> tuple[int, int]:
    u = int((x - origin_x) * scale)
    v = int(h - (z - origin_z) * scale)
    return u, v


def _darken(rgb: tuple[int, int, int], light: float) -> tuple[int, int, int]:
    return tuple(int(max(0, min(255, c * light))) for c in rgb)  # type: ignore[return-value]


def render_views(
    pose: ArmPose,
    *,
    block: tuple[float, float, float],
    bowl: tuple[float, float, float],
    bowl_radius: float,
    block_size: float,
    gripped: bool,
    light: float,
    width: int = 320,
    height: int = 240,
    block_rgb: tuple[int, int, int] = (200, 48, 48),
    bowl_rgb: tuple[int, int, int] = (40, 90, 190),
) -> dict[str, np.ndarray]:
    front = _render_front(
        pose,
        block=block,
        bowl=bowl,
        bowl_radius=bowl_radius,
        block_size=block_size,
        light=light,
        width=width,
        height=height,
        block_rgb=block_rgb,
        bowl_rgb=bowl_rgb,
    )
    wrist = _render_wrist(
        pose,
        block=block,
        bowl=bowl,
        bowl_radius=bowl_radius,
        block_size=block_size,
        gripped=gripped,
        light=light,
        width=width,
        height=height,
        block_rgb=block_rgb,
        bowl_rgb=bowl_rgb,
    )
    return {"front": front, "wrist": wrist}


def _render_front(
    pose: ArmPose,
    *,
    block: tuple[float, float, float],
    bowl: tuple[float, float, float],
    bowl_radius: float,
    block_size: float,
    light: float,
    width: int,
    height: int,
    block_rgb: tuple[int, int, int],
    bowl_rgb: tuple[int, int, int],
) -> np.ndarray:
    bg = _darken((214, 204, 186), light)
    table = _darken((176, 142, 96), light)
    arm = _darken((70, 74, 82), light)
    img = Image.new("RGB", (width, height), bg)
    draw = ImageDraw.Draw(img)
    scale = width / 0.50
    origin_x, origin_z = -0.04, -0.02

    def p(x: float, z: float) -> tuple[int, int]:
        return _px(x, z, origin_x=origin_x, origin_z=origin_z, scale=scale, h=height)

    # Table: x extent, z=0
    a, b = p(0.06, 0.0), p(0.36, 0.0)
    draw.rectangle([a[0], b[1] - 8, b[0], height - 4], fill=table)
    # Bowl and block use x as horizontal (ignore y for this orthographic "front")
    # Mix x with a bit of y so two objects at same x still separate.
    def xz(obj: tuple[float, float, float]) -> tuple[float, float]:
        return obj[0] + 0.15 * obj[1], obj[2]

    bx, bz = xz(bowl)
    br = int(bowl_radius * scale)
    c = p(bx, bz)
    draw.ellipse([c[0] - br, c[1] - br // 3, c[0] + br, c[1] + br // 3], fill=_darken(bowl_rgb, light))

    kx, kz = xz(block)
    hs = int(block_size * scale / 2)
    k = p(kx, kz)
    draw.rectangle([k[0] - hs, k[1] - hs, k[0] + hs, k[1] + hs], fill=_darken(block_rgb, light))

    pts = [p(pose.shoulder[0], pose.shoulder[2]), p(pose.elbow[0], pose.elbow[2]),
           p(pose.wrist[0], pose.wrist[2]), p(pose.ee[0], pose.ee[2])]
    draw.line(pts, fill=arm, width=8)
    for pt in pts:
        draw.ellipse([pt[0] - 5, pt[1] - 5, pt[0] + 5, pt[1] + 5], fill=arm)

    g = pose.joints["gripper"] / 100.0
    ee = p(pose.ee[0], pose.ee[2])
    gap = int(4 + 10 * g)
    draw.line([(ee[0] - gap, ee[1]), (ee[0] - gap, ee[1] + 16)], fill=arm, width=3)
    draw.line([(ee[0] + gap, ee[1]), (ee[0] + gap, ee[1] + 16)], fill=arm, width=3)
    return np.asarray(img, dtype=np.uint8)


def _render_wrist(
    pose: ArmPose,
    *,
    block: tuple[float, float, float],
    bowl: tuple[float, float, float],
    bowl_radius: float,
    block_size: float,
    gripped: bool,
    light: float,
    width: int,
    height: int,
    block_rgb: tuple[int, int, int],
    bowl_rgb: tuple[int, int, int],
) -> np.ndarray:
    bg = _darken((30, 30, 34), light)
    table = _darken((176, 142, 96), light)
    img = Image.new("RGB", (width, height), bg)
    draw = ImageDraw.Draw(img)
    # Looking down from the EE: table XY centered on EE.
    scale = width / 0.22
    ex, ey, _ = pose.ee

    def p(x: float, y: float) -> tuple[int, int]:
        u = int(width / 2 + (x - ex) * scale)
        v = int(height / 2 + (y - ey) * scale)
        return u, v

    # Table fill
    draw.rectangle([0, 0, width, height], fill=table)
    c = p(bowl[0], bowl[1])
    br = int(bowl_radius * scale)
    draw.ellipse([c[0] - br, c[1] - br, c[0] + br, c[1] + br], fill=_darken(bowl_rgb, light))
    k = p(block[0], block[1])
    hs = int(block_size * scale / 2)
    draw.rectangle([k[0] - hs, k[1] - hs, k[0] + hs, k[1] + hs], fill=_darken(block_rgb, light))

    # Gripper overlay in image center
    g = pose.joints["gripper"] / 100.0
    gap = int(8 + 28 * g)
    cx, cy = width // 2, height // 2
    arm = _darken((210, 210, 214), light)
    draw.rectangle([cx - gap - 8, cy - 40, cx - gap, cy + 40], fill=arm)
    draw.rectangle([cx + gap, cy - 40, cx + gap + 8, cy + 40], fill=arm)
    if gripped:
        draw.rectangle([cx - hs, cy - hs, cx + hs, cy + hs], fill=_darken(block_rgb, light))
    # Vignette ring
    draw.ellipse([8, 8, width - 8, height - 8], outline=_darken((20, 20, 20), light), width=6)
    return np.asarray(img, dtype=np.uint8)


def save_jpeg(array: np.ndarray, path) -> None:
    Image.fromarray(array).save(path, quality=85)
