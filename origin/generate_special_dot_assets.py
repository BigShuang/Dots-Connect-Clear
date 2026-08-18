"""Generate complete, consistently named colour variants for special dots."""

from __future__ import annotations

import colorsys
from collections import Counter
from pathlib import Path

from PIL import Image

from util import ASSETS_DIR


COLOUR_NAMES = ("coral", "blue", "purple", "gold", "green")


def load_basic_colours(dots: Path) -> dict[str, tuple[int, int, int]]:
    """Read the authoritative dominant RGB value from every BasicDot asset."""
    colours: dict[str, tuple[int, int, int]] = {}
    for name in COLOUR_NAMES:
        image = Image.open(dots / "basic" / f"{name}.png").convert("RGBA")
        visible = Counter(
            (red, green, blue)
            for red, green, blue, alpha in image.getdata()
            if alpha > 128
        )
        colours[name] = visible.most_common(1)[0][0]
    return colours


def recolour_flat(source: Path, destination: Path, colour: tuple[int, int, int]) -> None:
    """Replace visible RGB values while preserving the source alpha mask."""
    image = Image.open(source).convert("RGBA")
    pixels = [(*colour, alpha) for _red, _green, _blue, alpha in image.getdata()]
    image.putdata(pixels)
    destination.parent.mkdir(parents=True, exist_ok=True)
    image.save(destination)


def recolour_hue(source: Path, destination: Path, colour: tuple[int, int, int]) -> None:
    """Use the exact BasicDot RGB for dark arms and tint the highlights."""
    image = Image.open(source).convert("RGBA")
    output: list[tuple[int, int, int, int]] = []
    for red, green, blue, alpha in image.getdata():
        if alpha == 0:
            output.append((0, 0, 0, 0))
            continue
        _hue, lightness, _saturation = colorsys.rgb_to_hls(
            red / 255, green / 255, blue / 255
        )
        if lightness < 0.65:
            output.append((*colour, alpha))
            continue
        white_mix = max(0.55, min(0.82, (lightness - 0.55) / 0.40))
        highlighted = tuple(
            round(channel + (255 - channel) * white_mix) for channel in colour
        )
        output.append((*highlighted, alpha))
    image.putdata(output)
    destination.parent.mkdir(parents=True, exist_ok=True)
    image.save(destination)


def generate() -> None:
    dots = ASSETS_DIR / "dots"
    colours = load_basic_colours(dots)
    flat_families = {
        "companion": dots / "companion" / "coral.png",
        "flower": dots / "flower" / "coral.png",
    }
    for family, source in flat_families.items():
        for name, colour in colours.items():
            recolour_flat(source, dots / family / f"{name}.png", colour)

    swirl_source = dots / "swirl" / "coral.png"
    for name, colour in colours.items():
        recolour_hue(swirl_source, dots / "swirl" / f"{name}.png", colour)

    beam_sources = {
        "horizontal": dots / "beam" / "horizontal" / "coral.png",
        "vertical": dots / "beam" / "vertical" / "coral.png",
        "cross": dots / "beam" / "cross" / "coral.png",
    }
    for direction, source in beam_sources.items():
        for name, colour in colours.items():
            recolour_flat(source, dots / "beam" / direction / f"{name}.png", colour)


if __name__ == "__main__":
    generate()
