import random
import sys
from pathlib import Path
import unittest


STAGE1 = Path(__file__).resolve().parents[1]
if str(STAGE1) not in sys.path:
    sys.path.insert(0, str(STAGE1))

from dot import BasicDot, FlowerDot
from factory import DEFAULT_DOT_TYPES, DOT_KINDS, DotFactory


class DotFactoryTest(unittest.TestCase):
    def test_seeded_factories_are_repeatable(self) -> None:
        first = DotFactory(rng=random.Random(42))
        second = DotFactory(rng=random.Random(42))
        first_values = [first.create_dot().kind for _ in range(12)]
        second_values = [second.create_dot().kind for _ in range(12)]
        self.assertEqual(first_values, second_values)

    def test_default_factory_creates_configured_stage_two_mix(self) -> None:
        factory = DotFactory(rng=random.Random(1))
        dots = [factory.create_dot() for _ in range(200)]
        configured_types = tuple(dot_type for dot_type, _weight in DEFAULT_DOT_TYPES)
        self.assertTrue(all(isinstance(dot, configured_types) for dot in dots))
        self.assertTrue(any(not isinstance(dot, BasicDot) for dot in dots))

    def test_registration_can_select_one_dot_type(self) -> None:
        factory = DotFactory(enabled_dot_types=[(FlowerDot, 1)])
        self.assertIsInstance(factory.create_dot("blue"), FlowerDot)

    def test_unknown_kind_is_rejected(self) -> None:
        with self.assertRaises(ValueError):
            DotFactory().create_dot("turquoise")


if __name__ == "__main__":
    unittest.main()
