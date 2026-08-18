from __future__ import annotations

import sys
from pathlib import Path
from collections import Counter
import unittest

from PIL import Image


SRC = Path(__file__).resolve().parents[1]
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from util import ASSETS_DIR
from dot import BasicDot, CompanionDot, SwirlDot
from view import dot_asset_path


class SpecialDotAssetsTest(unittest.TestCase):
    def test_swirl_dark_colour_matches_basic_dot_exactly(self) -> None:
        for colour in ("coral", "blue", "purple", "gold", "green"):
            dominant = []
            for family in ("basic", "swirl"):
                with Image.open(
                    ASSETS_DIR / "dots" / family / f"{colour}.png"
                ) as image:
                    dominant.append(
                        Counter(
                            (red, green, blue)
                            for red, green, blue, alpha in image.convert("RGBA").getdata()
                            if alpha > 128
                        ).most_common(1)[0][0]
                    )
            self.assertEqual(dominant[0], dominant[1], colour)

    def test_implemented_dot_types_use_their_generated_assets(self) -> None:
        self.assertEqual(
            dot_asset_path(BasicDot("blue")),
            ASSETS_DIR / "dots" / "basic" / "blue.png",
        )
        self.assertEqual(
            dot_asset_path(CompanionDot("purple")),
            ASSETS_DIR / "dots" / "companion" / "purple.png",
        )
        self.assertEqual(
            dot_asset_path(SwirlDot("gold")),
            ASSETS_DIR / "dots" / "swirl" / "gold.png",
        )

    def test_all_semantic_colour_variants_exist(self) -> None:
        colours = {"coral", "blue", "purple", "gold", "green"}
        directories = [
            ASSETS_DIR / "dots" / "companion",
            ASSETS_DIR / "dots" / "flower",
            ASSETS_DIR / "dots" / "swirl",
            ASSETS_DIR / "dots" / "beam" / "horizontal",
            ASSETS_DIR / "dots" / "beam" / "vertical",
            ASSETS_DIR / "dots" / "beam" / "cross",
        ]
        for directory in directories:
            self.assertEqual(
                {path.stem for path in directory.glob("*.png")},
                colours,
                directory,
            )

    def test_special_assets_are_transparent_128_pixel_pngs(self) -> None:
        for family in ("companion", "flower", "swirl", "beam"):
            for path in (ASSETS_DIR / "dots" / family).rglob("*.png"):
                with Image.open(path) as image:
                    self.assertEqual(image.size, (128, 128), path)
                    self.assertEqual(image.mode, "RGBA", path)
                    self.assertEqual(image.getchannel("A").getextrema(), (0, 255), path)


if __name__ == "__main__":
    unittest.main()
