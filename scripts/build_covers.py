#!/usr/bin/env python3
"""Generate book covers (600x900) from data/books.json.

Each cover gets a dark gradient background tinted with the book's accent
color, a big decorative spine motif, the short title in Thai, the category
pill, and a footer line. Deterministic output keyed by book id.
"""

from __future__ import annotations

import json
import math
from pathlib import Path

from PIL import Image, ImageDraw, ImageFilter, ImageFont

ROOT = Path(__file__).resolve().parents[1]
CATALOG = ROOT / "data" / "books.json"
OUT_DIR = ROOT / "assets" / "covers"
W, H = 600, 900

FONT_BOLD = "/usr/share/fonts/truetype/noto/NotoSansThai-Bold.ttf"
FONT_REG = "/usr/share/fonts/truetype/noto/NotoSansThai-Regular.ttf"


def hex_to_rgb(value: str) -> tuple[int, int, int]:
    value = value.lstrip("#")
    return tuple(int(value[i:i + 2], 16) for i in (0, 2, 4))


def darken(rgb: tuple[int, int, int], factor: float) -> tuple[int, int, int]:
    return tuple(max(0, int(c * factor)) for c in rgb)


def lighten(rgb: tuple[int, int, int], factor: float) -> tuple[int, int, int]:
    return tuple(min(255, int(c + (255 - c) * factor)) for c in rgb)


def load_font(path: str, size: int) -> ImageFont.FreeTypeFont:
    return ImageFont.truetype(path, size)


def make_background(accent: tuple[int, int, int]) -> Image.Image:
    base = Image.new("RGB", (W, H))
    top = darken(accent, 0.16)
    bottom = darken(accent, 0.05)
    for y in range(H):
        t = y / (H - 1)
        r = int(top[0] + (bottom[0] - top[0]) * t)
        g = int(top[1] + (bottom[1] - top[1]) * t)
        b = int(top[2] + (bottom[2] - top[2]) * t)
        ImageDraw.Draw(base).line([(0, y), (W, y)], fill=(r, g, b))
    return base


def draw_orbs(img: Image.Image, accent: tuple[int, int, int]) -> Image.Image:
    layer = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(layer)
    glow = lighten(accent, 0.25)
    # large soft accent orb top-right
    d.ellipse([W - 260, -180, W + 260, 340], fill=(*glow, 60))
    # smaller orb bottom-left
    d.ellipse([-140, H - 300, 220, H + 60], fill=(*glow, 45))
    layer = layer.filter(ImageFilter.GaussianBlur(radius=60))
    return Image.alpha_composite(img.convert("RGBA"), layer)


def draw_spine(img: Image.Image, accent: tuple[int, int, int]) -> Image.Image:
    d = ImageDraw.Draw(img)
    # left spine band
    band = darken(accent, 0.35)
    d.rectangle([0, 0, 34, H], fill=band)
    d.rectangle([34, 0, 40, H], fill=lighten(accent, 0.15))
    # decorative thin rules
    d.line([(70, 120), (W - 70, 120)], fill=(*lighten(accent, 0.4), 120), width=2)
    d.line([(70, H - 150), (W - 70, H - 150)], fill=(*lighten(accent, 0.4), 120), width=2)
    return img


def wrap_text(text: str, font: ImageFont.FreeTypeFont, max_width: int) -> list[str]:
    words = text.split()
    lines: list[str] = []
    current = ""
    for word in words:
        candidate = f"{current} {word}".strip()
        if ImageDraw.Draw(Image.new("RGB", (10, 10))).textlength(candidate, font=font) <= max_width:
            current = candidate
        else:
            if current:
                lines.append(current)
            current = word
    if current:
        lines.append(current)
    return lines


def draw_cover(book: dict) -> Path:
    accent = hex_to_rgb(book["accent"])
    img = make_background(accent)
    img = draw_orbs(img, accent)
    img = draw_spine(img, accent)
    d = ImageDraw.Draw(img)

    pad = 70
    usable_w = W - pad * 2

    # category pill
    cat_font = load_font(FONT_REG, 30)
    cat_text = book["category"]
    cat_w = d.textlength(cat_text, font=cat_font)
    pill_w = cat_w + 48
    pill_h = 54
    pill_y = 150
    d.rounded_rectangle([pad, pill_y, pad + pill_w, pill_y + pill_h], radius=pill_h // 2,
                        outline=lighten(accent, 0.35), width=3)
    d.text((pad + 24, pill_y + 9), cat_text, font=cat_font, fill=lighten(accent, 0.45))

    # title
    title_font = load_font(FONT_BOLD, 56)
    lines = wrap_text(book["short_title"], title_font, usable_w)
    while len(lines) > 5:
        size = title_font.size - 4
        title_font = load_font(FONT_BOLD, size)
        lines = wrap_text(book["short_title"], title_font, usable_w)
    y = 250
    for line in lines:
        d.text((pad, y), line, font=title_font, fill=(245, 240, 230))
        y += int(title_font.size * 1.35)

    # accent divider under title
    d.line([(pad, y + 20), (pad + 120, y + 20)], fill=lighten(accent, 0.4), width=6)

    # footer line
    foot_font = load_font(FONT_REG, 28)
    foot = "ชั้นหนังสือแห่งความรู้"
    d.text((pad, H - 110), foot, font=foot_font, fill=lighten(accent, 0.3))
    sub_font = load_font(FONT_REG, 22)
    d.text((pad, H - 70), "Knowledge Shelf · Curated Guide", font=sub_font, fill=(*lighten(accent, 0.35),))

    out_path = OUT_DIR / f"{book['id']}.png"
    img.convert("RGB").save(out_path, "PNG", optimize=True)
    return out_path


def main() -> None:
    books = json.loads(CATALOG.read_text(encoding="utf-8"))
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    for book in books:
        path = draw_cover(book)
        print(f"wrote {path}")


if __name__ == "__main__":
    main()
