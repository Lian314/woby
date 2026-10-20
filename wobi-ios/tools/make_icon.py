"""生成卧笔 App 图标（1024x1024，无透明通道）。

会同时输出两个备选：
    tools/icon-dark.png   墨底白字
    tools/icon-paper.png  纸底墨字（默认采用）
改 DEFAULT 可切换。

用法：
    python tools/make_icon.py
"""

from __future__ import annotations

import random
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageFont

ROOT = Path(__file__).resolve().parent.parent
ASSETS = ROOT / "Wobi" / "Assets.xcassets" / "AppIcon.appiconset"
OUT = ASSETS / "AppIcon.png"
TOOLS = ROOT / "tools"

SIZE = 1024
FONT_PATH = Path(r"C:\Windows\Fonts\STKAITI.TTF")
DEFAULT = "paper"  # dark | paper

PAPER = (246, 239, 226)
INK = (20, 22, 26)
SEAL = (170, 57, 44)


def noise_layer(sigma: float, blur: float = 1.0) -> Image.Image:
    rng = np.random.default_rng(20261020)
    noise = rng.normal(0, 1, (SIZE, SIZE)).astype(np.float32)
    img = Image.fromarray(((noise * 0.15 + 0.5) * 255).clip(0, 255).astype(np.uint8))
    img = img.filter(ImageFilter.GaussianBlur(blur))
    arr = np.array(img, dtype=np.float32)
    arr = (arr - arr.mean()) / (arr.std() + 1e-6) * sigma
    return Image.fromarray(np.clip(arr + 128, 0, 255).astype(np.uint8), "L")


def background(dark: bool) -> Image.Image:
    yy = np.linspace(0.0, 1.0, SIZE, dtype=np.float32)[:, None]
    xx = np.linspace(0.0, 1.0, SIZE, dtype=np.float32)[None, :]
    cx, cy = (xx - 0.5) * 2, (yy - 0.5) * 2
    radius = np.sqrt(cx**2 + cy**2)

    if dark:
        inner = np.array([43, 47, 54], dtype=np.float32)
        outer = np.array([13, 15, 18], dtype=np.float32)
    else:
        inner = np.array([250, 245, 235], dtype=np.float32)
        outer = np.array([226, 214, 193], dtype=np.float32)

    glow = np.clip(1.0 - radius * 0.55, 0.0, 1.0)[..., None]
    grad = outer[None, None, :] + (inner - outer)[None, None, :] * glow

    grain = np.array(noise_layer(1.8 if dark else 1.3), dtype=np.float32) - 128.0
    grad += grain[..., None]

    wash = np.array(noise_layer(4.0, blur=24.0), dtype=np.float32) - 128.0
    grad += wash[..., None] * (0.7 if dark else 0.45)

    return Image.fromarray(np.clip(grad, 0, 255).astype(np.uint8), "RGB")


def draw_centered_text(
    image: Image.Image,
    text: str,
    font: ImageFont.FreeTypeFont,
    fill: tuple[int, int, int],
    offset_y: int = 0,
) -> None:
    draw = ImageDraw.Draw(image)
    box = draw.textbbox((0, 0), text, font=font)
    width = box[2] - box[0]
    height = box[3] - box[1]
    x = (SIZE - width) / 2 - box[0]
    y = (SIZE - height) / 2 - box[1] + offset_y
    draw.text((x, y), text, font=font, fill=fill)


def draw_seal(image: Image.Image, letter: str, box_size: int, margin: int) -> None:
    size = box_size
    seal = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    draw = ImageDraw.Draw(seal)
    draw.rounded_rectangle([0, 0, size - 1, size - 1], radius=18, fill=SEAL + (255,))

    rnd = random.Random(11)
    for _ in range(45):
        x, y = rnd.uniform(8, size - 8), rnd.uniform(8, size - 8)
        r = rnd.uniform(1.0, 3.2)
        draw.ellipse([x, y, x + r, y + r], fill=SEAL + (0,))

    if FONT_PATH.exists():
        font = ImageFont.truetype(str(FONT_PATH), int(size * 0.6))
        box = draw.textbbox((0, 0), letter, font=font)
        tw, th = box[2] - box[0], box[3] - box[1]
        draw.text(
            ((size - tw) / 2 - box[0], (size - th) / 2 - box[1]),
            letter,
            font=font,
            fill=PAPER + (255,),
        )

    seal = seal.rotate(-4, resample=Image.BICUBIC, expand=False)
    image.paste(seal, (SIZE - margin - size, SIZE - margin - size), seal)


def build(dark: bool) -> Image.Image:
    image = background(dark)

    if FONT_PATH.exists():
        font = ImageFont.truetype(str(FONT_PATH), 600)
    else:
        font = ImageFont.load_default()

    color = PAPER if dark else INK
    draw_centered_text(image, "卧", font, color, offset_y=-18)
    draw_seal(image, "笔", box_size=168, margin=72)

    grain = np.array(noise_layer(1.0), dtype=np.float32) - 128.0
    arr = np.array(image, dtype=np.float32) + grain[..., None] * 0.35
    return Image.fromarray(np.clip(arr, 0, 255).astype(np.uint8), "RGB")


def main() -> None:
    TOOLS.mkdir(parents=True, exist_ok=True)
    dark = build(True)
    paper = build(False)
    dark.save(TOOLS / "icon-dark.png", "PNG")
    paper.save(TOOLS / "icon-paper.png", "PNG")

    chosen = dark if DEFAULT == "dark" else paper
    chosen.save(OUT, "PNG")
    chosen.save(TOOLS / "icon-preview.png", "PNG")
    print(f"wrote {OUT} ({chosen.size[0]}x{chosen.size[1]}, {chosen.mode})")


if __name__ == "__main__":
    main()
