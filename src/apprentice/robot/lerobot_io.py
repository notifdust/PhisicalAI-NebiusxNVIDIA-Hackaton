"""Optional LeRobot imports. Bring-up commands work without this package."""

from __future__ import annotations

from typing import Any


def follower_types() -> tuple[Any, Any]:
    try:
        from lerobot.robots.so101_follower import SO101Follower, SO101FollowerConfig

        return SO101Follower, SO101FollowerConfig
    except ImportError:
        from lerobot.robots.so_follower import SO101Follower, SO101FollowerConfig

        return SO101Follower, SO101FollowerConfig
