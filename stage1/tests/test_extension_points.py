import random
import sys
from pathlib import Path
import unittest


STAGE1 = Path(__file__).resolve().parents[1]
if str(STAGE1) not in sys.path:
    sys.path.insert(0, str(STAGE1))

from dot import BasicDot
from factory import DotFactory
from game import DotGame


class ExampleFutureDot(BasicDot):
    """A test double proving Stage 2 can override the activation hook."""

    def activate(self, grid, position):
        affected = super().activate(grid, position)
        affected.update(grid.neighbours(position))
        return affected


class ExtensionPointTest(unittest.TestCase):
    def test_factory_can_be_injected_without_changing_dot_grid(self) -> None:
        factory = DotFactory(rng=random.Random(2), dot_class=ExampleFutureDot)
        game = DotGame(
            rows=3,
            columns=3,
            objectives={kind: 9 for kind in factory.kinds},
            rng=random.Random(2),
            factory=factory,
        )
        self.assertTrue(
            all(
                isinstance(game.grid.dot_at(position), ExampleFutureDot)
                for position in game.grid.positions()
            )
        )

    def test_future_dot_can_extend_activation_without_replacing_game_flow(self) -> None:
        factory = DotFactory(rng=random.Random(2), dot_class=ExampleFutureDot)
        game = DotGame(
            rows=3,
            columns=3,
            objectives={kind: 9 for kind in factory.kinds},
            rng=random.Random(2),
            factory=factory,
        )
        for position in game.grid.positions():
            game.grid.set_dot(position, BasicDot("blue"))
        game.grid.set_dot((1, 1), ExampleFutureDot("blue"))

        game.start_selection((1, 1))
        game.extend_selection((1, 2))
        result = game.finish_selection()

        self.assertEqual(result.removed, 5)


if __name__ == "__main__":
    unittest.main()
