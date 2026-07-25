#!/usr/bin/env python3
"""
Generates the KeepMeUp icon assets (menu bar PNGs + app .icns).

Run once at authoring time — the output PNGs/icns are checked into git under
assets/, and install.sh just copies them into the app bundle. This script is
NOT run as part of install.sh; it requires Pillow, which isn't a runtime
dependency of the app itself.

Usage: python3 assets/generate_icons.py
"""
import math
import os
import subprocess
import sys

from PIL import Image, ImageDraw, ImageFilter

ASSETS_DIR = os.path.dirname(os.path.abspath(__file__))

# Menu bar icons are drawn at 4x (176px) and downsampled to 44px (22pt @2x)
# for clean antialiasing on retina displays.
SUPERSAMPLE = 176
MENU_SIZE = 44

OUTER_R = 0.42   # star outer radius, fraction of canvas
INNER_R = 0.19   # star inner radius (how jagged the points are)
POINTS = 8       # number of star points

ACCENT_COLOR = (255, 176, 32, 255)   # warm amber "lit bulb" color
GLOW_COLOR = (255, 200, 80, 110)     # soft glow behind the lit star
BLACK = (0, 0, 0, 255)


def star_polygon(size, outer_r, inner_r, points, rotation=-90):
    """Return vertex list for a jagged N-point star centered in a size×size canvas."""
    cx = cy = size / 2
    verts = []
    step = 360 / (points * 2)
    for i in range(points * 2):
        angle = math.radians(rotation + i * step)
        r = outer_r if i % 2 == 0 else inner_r
        r_px = r * size
        verts.append((cx + r_px * math.cos(angle), cy + r_px * math.sin(angle)))
    return verts


def render(filled, glow=False):
    img = Image.new("RGBA", (SUPERSAMPLE, SUPERSAMPLE), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    poly = star_polygon(SUPERSAMPLE, OUTER_R, INNER_R, POINTS)

    if glow:
        glow_img = Image.new("RGBA", (SUPERSAMPLE, SUPERSAMPLE), (0, 0, 0, 0))
        glow_draw = ImageDraw.Draw(glow_img)
        glow_poly = star_polygon(SUPERSAMPLE, OUTER_R * 1.35, INNER_R * 1.35, POINTS)
        glow_draw.polygon(glow_poly, fill=GLOW_COLOR)
        glow_img = glow_img.filter(ImageFilter.GaussianBlur(SUPERSAMPLE * 0.05))
        img = Image.alpha_composite(img, glow_img)
        draw = ImageDraw.Draw(img)

    color = ACCENT_COLOR if glow else BLACK
    if filled:
        draw.polygon(poly, fill=color)
    else:
        draw.polygon(poly, outline=color, width=int(SUPERSAMPLE * 0.045))

    img = img.resize((MENU_SIZE, MENU_SIZE), Image.LANCZOS)
    return img


def build_menu_icons():
    icon_off = render(filled=False, glow=False)
    icon_off.save(os.path.join(ASSETS_DIR, "icon_off.png"))

    icon_device_awake = render(filled=True, glow=False)
    icon_device_awake.save(os.path.join(ASSETS_DIR, "icon_device_awake.png"))

    icon_screen_awake = render(filled=True, glow=True)
    icon_screen_awake.save(os.path.join(ASSETS_DIR, "icon_screen_awake.png"))

    print("Wrote icon_off.png, icon_device_awake.png, icon_screen_awake.png")


def build_app_icon():
    """Build AppIcon.icns from the filled (non-glow) star at standard sizes."""
    iconset_dir = os.path.join(ASSETS_DIR, "AppIcon.iconset")
    os.makedirs(iconset_dir, exist_ok=True)

    # macOS iconset naming convention: icon_<size>x<size>[@2x].png
    sizes = [16, 32, 128, 256, 512]
    for size in sizes:
        img = Image.new("RGBA", (size * 4, size * 4), (0, 0, 0, 0))
        draw = ImageDraw.Draw(img)
        poly = star_polygon(size * 4, OUTER_R, INNER_R, POINTS)
        draw.polygon(poly, fill=ACCENT_COLOR)
        img = img.resize((size, size), Image.LANCZOS)
        img.save(os.path.join(iconset_dir, f"icon_{size}x{size}.png"))

        img2x = Image.new("RGBA", (size * 8, size * 8), (0, 0, 0, 0))
        draw2x = ImageDraw.Draw(img2x)
        poly2x = star_polygon(size * 8, OUTER_R, INNER_R, POINTS)
        draw2x.polygon(poly2x, fill=ACCENT_COLOR)
        img2x = img2x.resize((size * 2, size * 2), Image.LANCZOS)
        img2x.save(os.path.join(iconset_dir, f"icon_{size}x{size}@2x.png"))

    icns_path = os.path.join(ASSETS_DIR, "AppIcon.icns")
    subprocess.run(
        ["iconutil", "-c", "icns", iconset_dir, "-o", icns_path],
        check=True,
    )

    # Clean up the intermediate .iconset directory — only the .icns is needed.
    import shutil
    shutil.rmtree(iconset_dir)

    print(f"Wrote {icns_path}")


if __name__ == "__main__":
    build_menu_icons()
    build_app_icon()
