import random
import sys
from pathlib import Path
import unittest


STAGE1 = Path(__file__).resolve().parents[1]
if str(STAGE1) not in sys.path:
    sys.path.insert(0, str(STAGE1))

from dot import BasicDot
from factory import DOT_KINDS, DotFactory


class DotFactoryTest(unittest.TestCase):
    def test_seeded_factories_are_repeatable(self) -> None:
        first = DotFactory(rng=random.Random(42))
        second = DotFactory(rng=random.Random(42))
        first_values = [first.create_dot().kind for _ in range(12)]
        second_values = [second.create_dot().kind for _ in range(12)]
        self.assertEqual(first_values, second_values)

    def test_factory_creates_basic_dots_in_stage_one(self) -> None:
        factory = DotFactory(rng=random.Random(1))
        dots = [factory.create_dot() for _ in range(20)]
        self.assertTrue(all(isinstance(dot, BasicDot) for dot in dots))
        self.assertTrue(all(dot.kind in DOT_KINDS for dot in dots))

    def test_unknown_kind_is_rejected(self) -> None:
        with self.assertRaises(ValueError):
            DotFactory().create_dot("turquoise")


if __name__ == "__main__":
    unittest.main()
