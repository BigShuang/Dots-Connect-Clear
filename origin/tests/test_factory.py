from __future__ import annotations

import random
import sys
from pathlib import Path
import unittest


SRC = Path(__file__).resolve().parents[1]
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from factory import DOT_KINDS, DotFactory


class DotFactoryTest(unittest.TestCase):
    def test_seeded_factory_is_repeatable(self) -> None:
        first = DotFactory(rng=random.Random(42))
        second = DotFactory(rng=random.Random(42))
        self.assertEqual(
            [first.create_basic().kind for _ in range(12)],
            [second.create_basic().kind for _ in range(12)],
        )

    def test_created_kinds_are_supported(self) -> None:
        factory = DotFactory(rng=random.Random(1))
        self.assertTrue(all(factory.create_basic().kind in DOT_KINDS for _ in range(30)))

    def test_unknown_explicit_kind_is_rejected(self) -> None:
        with self.assertRaises(ValueError):
            DotFactory().create_basic("turquoise")


if __name__ == "__main__":
    unittest.main()
