"""Generate deterministic, antialiased PNG assets for the four basic dots."""

from __future__ import annotations

from pathlib import Path

from PIL import Image, ImageDraw

from util import ASSETS_DIR


DOT_COLOURS = {
    "coral": "#a30e15",
    "blue": "#508ebf",
    "gold": "#f9bf3b",
    "purple": "#493047",
}

OUTPUT_DIR = ASSETS_DIR / "dots" / "basic"
FINAL_SIZE = 256
SUPERSAMPLING = 4
EDGE_MARGIN = 8


def generate_dot_asset(name: str, colour: str) -> Path:
    """Create one transparent, solid-colour dot PNG and return its path."""
    large_size = FINAL_SIZE * SUPERSAMPLING
    margin = EDGE_MARGIN * SUPERSAMPLING
    image = Image.new("RGBA", (large_size, large_size), (0, 0, 0, 0))
    ImageDraw.Draw(image).ellipse(
        (margin, margin, large_size - margin - 1, large_size - margin - 1),
        fill=colour,
    )
    image = image.resize(
        (FINAL_SIZE, FINAL_SIZE),
        resample=Image.Resampling.LANCZOS,
    )
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    output = OUTPUT_DIR / f"{name}.png"
    image.save(output, optimize=True)
    return output


def main() -> None:
    for name, colour in DOT_COLOURS.items():
        print(generate_dot_asset(name, colour))


if __name__ == "__main__":
    main()
