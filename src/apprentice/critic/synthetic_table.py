"""A tiny tabletop scene for Cosmos Reasoner hello-world when no camera frame exists."""

from __future__ import annotations

from pathlib import Path

from PIL import Image, ImageDraw


def write_synthetic_table(path: Path | None = None) -> Path:
    dest = path or Path("data") / "synthetic_table.jpg"
    dest.parent.mkdir(parents=True, exist_ok=True)
    img = Image.new("RGB", (640, 480), (210, 198, 176))
    draw = ImageDraw.Draw(img)
    draw.rectangle([40, 80, 600, 440], fill=(186, 154, 110), outline=(90, 70, 40), width=4)
    draw.ellipse([380, 220, 530, 360], fill=(40, 90, 180), outline=(20, 40, 90), width=3)
    draw.ellipse([120, 250, 200, 330], fill=(200, 40, 40), outline=(80, 10, 10), width=3)
    draw.rectangle([250, 40, 310, 200], fill=(70, 70, 80), outline=(20, 20, 20), width=3)
    img.save(dest, quality=90)
    return dest
