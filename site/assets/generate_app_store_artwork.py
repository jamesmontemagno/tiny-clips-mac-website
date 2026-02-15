from __future__ import annotations

import argparse
from dataclasses import dataclass
from pathlib import Path

from PIL import Image, ImageDraw, ImageFilter, ImageFont


@dataclass
class FeatureArtwork:
    output_name: str
    source_name: str
    eyebrow: str
    title: str
    subtitle: str


FEATURES: list[FeatureArtwork] = [
    FeatureArtwork(
        output_name="app-store-artwork-1.png",
        source_name="menu-bar.png",
        eyebrow="TINY CLIPS",
        title="Quick Menu Bar Access",
        subtitle="Start screenshots, video, and GIF in one click",
    ),
    FeatureArtwork(
        output_name="app-store-artwork-2.png",
        source_name="screenshot-edit.png",
        eyebrow="TINY CLIPS",
        title="Powerful Screenshot Editing",
        subtitle="Annotate and polish captures in seconds",
    ),
    FeatureArtwork(
        output_name="app-store-artwork-3.png",
        source_name="tinyclips-main.png",
        eyebrow="TINY CLIPS",
        title="Smart Video Trimming",
        subtitle="Trim and edit right after recording",
    ),
]


FONT_CANDIDATES = [
    "/System/Library/Fonts/Supplemental/Arial Bold.ttf",
    "/System/Library/Fonts/Supplemental/Helvetica.ttc",
]


def load_font(size: int) -> ImageFont.FreeTypeFont | ImageFont.ImageFont:
    for font_path in FONT_CANDIDATES:
        try:
            return ImageFont.truetype(font_path, size=size)
        except Exception:
            continue
    return ImageFont.load_default()


def wrap_lines(draw: ImageDraw.ImageDraw, text: str, font: ImageFont.ImageFont, max_width: int) -> list[str]:
    words = text.split()
    lines: list[str] = []
    current = ""
    for word in words:
        candidate = f"{current} {word}".strip()
        width = draw.textbbox((0, 0), candidate, font=font)[2]
        if width <= max_width or not current:
            current = candidate
        else:
            lines.append(current)
            current = word
    if current:
        lines.append(current)
    return lines


def draw_fit_text_block(
    draw: ImageDraw.ImageDraw,
    text: str,
    x: int,
    y: int,
    max_width: int,
    max_height: int,
    start_size: int,
    min_size: int,
    fill: tuple[int, int, int],
    line_spacing: int,
) -> int:
    for size in range(start_size, min_size - 1, -2):
        font = load_font(size)
        lines = wrap_lines(draw, text, font, max_width)
        line_height = draw.textbbox((0, 0), "Ag", font=font)[3]
        total = len(lines) * line_height + (len(lines) - 1) * line_spacing
        if total <= max_height:
            cursor_y = y
            for line in lines:
                draw.text((x, cursor_y), line, font=font, fill=fill)
                cursor_y += line_height + line_spacing
            return cursor_y

    font = load_font(min_size)
    lines = wrap_lines(draw, text, font, max_width)
    line_height = draw.textbbox((0, 0), "Ag", font=font)[3]
    cursor_y = y
    for line in lines:
        if cursor_y + line_height > y + max_height:
            break
        draw.text((x, cursor_y), line, font=font, fill=fill)
        cursor_y += line_height + line_spacing
    return cursor_y


def make_background(width: int, height: int) -> Image.Image:
    image = Image.new("RGB", (width, height), "#070b14")
    draw = ImageDraw.Draw(image)

    for row in range(height):
        t = row / (height - 1)
        red = int(8 + (22 - 8) * t)
        green = int(12 + (28 - 12) * t)
        blue = int(22 + (48 - 22) * t)
        draw.line([(0, row), (width, row)], fill=(red, green, blue))

    glows = [
        (int(width * 0.83), int(height * 0.16), int(height * 0.3), (72, 140, 255, 90)),
        (int(width * 0.2), int(height * 0.88), int(height * 0.33), (122, 86, 255, 78)),
    ]
    for cx, cy, radius, color in glows:
        glow = Image.new("RGBA", (width, height), (0, 0, 0, 0))
        glow_draw = ImageDraw.Draw(glow)
        glow_draw.ellipse((cx - radius, cy - radius, cx + radius, cy + radius), fill=color)
        glow = glow.filter(ImageFilter.GaussianBlur(int(height * 0.08)))
        image = Image.alpha_composite(image.convert("RGBA"), glow).convert("RGB")

    return image


def place_screenshot(base: Image.Image, screenshot: Image.Image, panel_box: tuple[int, int, int, int]) -> Image.Image:
    x1, y1, x2, y2 = panel_box
    panel_w = x2 - x1
    panel_h = y2 - y1

    base_rgba = base.convert("RGBA")
    panel = Image.new("RGBA", (panel_w, panel_h), (18, 24, 42, 226))
    panel_draw = ImageDraw.Draw(panel)

    corner = 28
    panel_draw.rounded_rectangle(
        (0, 0, panel_w - 1, panel_h - 1),
        radius=corner,
        fill=(18, 24, 42, 226),
        outline=(126, 152, 220, 185),
        width=2,
    )

    padding = 20
    inner_w = panel_w - padding * 2
    inner_h = panel_h - padding * 2

    shot = screenshot.copy()
    shot.thumbnail((inner_w, inner_h), Image.Resampling.LANCZOS)

    inner = Image.new("RGBA", (inner_w, inner_h), (8, 12, 22, 255))
    inner.paste(shot, ((inner_w - shot.width) // 2, (inner_h - shot.height) // 2))
    panel.paste(inner, (padding, padding))

    shadow = Image.new("RGBA", (panel_w + 34, panel_h + 34), (0, 0, 0, 0))
    shadow_draw = ImageDraw.Draw(shadow)
    shadow_draw.rounded_rectangle((16, 16, panel_w + 2, panel_h + 2), radius=corner + 4, fill=(0, 0, 0, 160))
    shadow = shadow.filter(ImageFilter.GaussianBlur(12))

    base_rgba.alpha_composite(shadow, (x1 - 10, y1 + 10))
    base_rgba.alpha_composite(panel, (x1, y1))
    return base_rgba.convert("RGB")


def render_one(feature: FeatureArtwork, assets_dir: Path, width: int, height: int) -> None:
    image = make_background(width, height)
    draw = ImageDraw.Draw(image)

    left_x = int(width * 0.05)
    left_w = int(width * 0.39)
    top_y = int(height * 0.24)

    eyebrow_font = load_font(34)
    draw.text((left_x, int(height * 0.18)), feature.eyebrow, font=eyebrow_font, fill=(170, 194, 255))

    title_bottom = draw_fit_text_block(
        draw,
        feature.title,
        x=left_x,
        y=top_y,
        max_width=left_w,
        max_height=120,
        start_size=68,
        min_size=50,
        fill=(255, 255, 255),
        line_spacing=6,
    )

    subtitle_y = title_bottom + 18
    draw_fit_text_block(
        draw,
        feature.subtitle,
        x=left_x,
        y=subtitle_y,
        max_width=left_w,
        max_height=130,
        start_size=32,
        min_size=24,
        fill=(188, 208, 248),
        line_spacing=6,
    )

    screenshot = Image.open(assets_dir / feature.source_name).convert("RGB")
    right_box = (
        int(width * 0.45),
        int(height * 0.1),
        int(width * 0.98),
        int(height * 0.9),
    )
    final = place_screenshot(image, screenshot, right_box)

    out_path = assets_dir / feature.output_name
    final.save(out_path, format="PNG", optimize=True)
    print(f"Wrote {out_path}")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Generate Tiny Clips App Store artwork.")
    parser.add_argument("--width", type=int, default=1440, help="Output image width")
    parser.add_argument("--height", type=int, default=900, help="Output image height")
    parser.add_argument("--assets-dir", type=Path, default=Path(__file__).parent, help="Assets directory")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    for feature in FEATURES:
        render_one(feature, args.assets_dir, args.width, args.height)


if __name__ == "__main__":
    main()
