import random
import sys
from pathlib import Path
import unittest

STAGE2 = Path(__file__).resolve().parents[1]
if str(STAGE2) not in sys.path:
    sys.path.insert(0, str(STAGE2))

from companion import (
    BuffaloCompanion, CaptainCompanion, EskimoCompanion, StarCompanion,
)
from dot import (
    AnchorDot, BasicDot, BeamDot, CompanionDot, FlowerDot, ShellDot, StarDot,
    SwirlDot, TurtleDot, WildcardDot,
)
from factory import DotFactory
from game import DotGame


class StageTwoFeatureTest(unittest.TestCase):
    def make_game(self, companion=None):
        factory = DotFactory(rng=random.Random(4), dot_class=BasicDot)
        return DotGame(rows=3, columns=3, moves=5,
                       objectives={kind: 20 for kind in factory.kinds},
                       rng=random.Random(4), factory=factory,
                       companion=companion)

    @staticmethod
    def fill(game, kind="blue"):
        for position in game.grid.positions():
            game.grid.set_dot(position, BasicDot(kind))

    def connect(self, game, first=(0, 0), second=(0, 1)):
        self.assertTrue(game.start_selection(first))
        self.assertTrue(game.extend_selection(second))
        return game.finish_selection()

    def test_flower_removes_orthogonal_neighbours(self):
        game = self.make_game()
        self.fill(game)
        game.grid.set_dot((1, 1), FlowerDot("blue"))
        result = self.connect(game, (1, 1), (1, 2))
        self.assertEqual(result.removed, 5)

    def test_all_beam_directions(self):
        game = self.make_game()
        self.fill(game)
        game.grid.set_dot((1, 1), BeamDot("blue", "horizontal"))
        self.assertEqual(self.connect(game, (1, 1), (1, 2)).removed, 3)
        self.fill(game)
        game.grid.set_dot((1, 1), BeamDot("blue", "vertical"))
        self.assertEqual(self.connect(game, (1, 1), (1, 2)).removed, 4)
        self.fill(game)
        game.grid.set_dot((1, 1), BeamDot("blue", "cross"))
        self.assertEqual(self.connect(game, (1, 1), (1, 2)).removed, 5)

    def test_factory_creates_seeded_beam_direction(self):
        first = DotFactory(rng=random.Random(7), dot_class=BasicDot)
        second = DotFactory(rng=random.Random(7), dot_class=BasicDot)
        first_beam = first.create_dot(kind="blue", dot_type=BeamDot)
        second_beam = second.create_dot(kind="blue", dot_type=BeamDot)
        self.assertEqual(first_beam.direction, second_beam.direction)
        self.assertIn(first_beam.direction, BeamDot.valid_directions)

    def test_beam_rejects_unknown_direction(self):
        with self.assertRaises(ValueError):
            BeamDot("blue", "diagonal")

    def test_swirl_recolours_eight_neighbours(self):
        game = self.make_game()
        self.fill(game, "gold")
        game.grid.set_dot((1, 1), SwirlDot("blue"))
        game.grid.set_dot((1, 2), BasicDot("blue"))
        self.connect(game, (1, 1), (1, 2))
        # The whole top row survives activation and was recoloured before gravity.
        self.assertTrue(all(game.grid.dot_at((1, column)).kind == "blue"
                            for column in range(3)))

    def test_star_removes_every_dot_of_its_colour(self):
        game = self.make_game()
        self.fill(game, "gold")
        game.grid.set_dot((0, 0), StarDot("blue"))
        game.grid.set_dot((0, 1), BasicDot("blue"))
        game.grid.set_dot((2, 2), BasicDot("blue"))
        result = self.connect(game, (0, 0), (0, 1))
        self.assertEqual(result.removed, 3)

    def test_wildcard_adopts_connection_colour(self):
        game = self.make_game()
        self.fill(game, "gold")
        game.grid.set_dot((0, 0), WildcardDot())
        game.grid.set_dot((0, 1), BasicDot("blue"))
        game.grid.set_dot((0, 2), BasicDot("gold"))
        self.assertTrue(game.start_selection((0, 0)))
        self.assertTrue(game.extend_selection((0, 1)))
        self.assertEqual(game.selection_kind, "blue")
        self.assertFalse(game.extend_selection((0, 2)))

    def test_turtle_hides_then_disappears_after_two_range_hits(self):
        game = self.make_game()
        self.fill(game)
        turtle = TurtleDot("blue")
        game.grid.set_dot((1, 0), turtle)
        self.assertEqual(turtle.asset_family, "turtle")
        game.grid.set_dot((1, 1), FlowerDot("blue"))
        self.connect(game, (1, 1), (1, 2))
        self.assertTrue(any(game.grid.dot_at(position) is turtle
                            for position in game.grid.positions()))
        self.assertEqual(turtle.hits_remaining, 1)
        self.assertEqual(turtle.asset_family, "shell")
        game.grid.set_dot((1, 1), FlowerDot("blue"))
        game.grid.set_dot((1, 2), BasicDot("blue"))
        self.connect(game, (1, 1), (1, 2))
        self.assertFalse(any(game.grid.dot_at(position) is turtle
                             for position in game.grid.positions()))

    def test_shell_starts_hidden_and_needs_one_range_hit(self):
        game = self.make_game()
        self.fill(game)
        shell = ShellDot("blue")
        game.grid.set_dot((1, 0), shell)
        self.assertEqual(shell.asset_family, "shell")
        self.assertEqual(shell.hits_remaining, 1)
        game.grid.set_dot((1, 1), FlowerDot("blue"))
        self.connect(game, (1, 1), (1, 2))
        self.assertFalse(any(game.grid.dot_at(position) is shell
                             for position in game.grid.positions()))

    def test_anchor_is_collected_at_segment_bottom(self):
        game = self.make_game()
        self.fill(game)
        game.grid.set_dot((2, 0), AnchorDot("blue"))
        self.connect(game, (0, 0), (0, 1))
        self.assertEqual(game.anchors_collected, 1)

    def test_companion_dot_charges_and_activates(self):
        companion = EskimoCompanion(charge_limit=2, swirl_count=1,
                                     rng=random.Random(2))
        game = self.make_game(companion)
        self.fill(game)
        game.grid.set_dot((0, 0), CompanionDot("blue"))
        game.grid.set_dot((0, 1), CompanionDot("blue"))
        self.connect(game)
        self.assertEqual(companion.charge, 0)
        self.assertTrue(any(isinstance(game.grid.dot_at(position), SwirlDot)
                            for position in game.grid.positions()))

    def test_star_companion_creates_star_after_charging(self):
        companion = StarCompanion(charge_limit=2, rng=random.Random(2))
        game = self.make_game(companion)
        self.fill(game)
        game.grid.set_dot((0, 0), CompanionDot("blue"))
        game.grid.set_dot((0, 1), CompanionDot("blue"))
        self.connect(game)
        stars = [game.grid.dot_at(position) for position in game.grid.positions()
                 if isinstance(game.grid.dot_at(position), StarDot)]
        self.assertEqual(len(stars), 1)
        self.assertEqual(stars[0].kind, "blue")

    def test_buffalo_companion_creates_wildcards_after_charging(self):
        companion = BuffaloCompanion(charge_limit=2, wildcard_count=2,
                                     rng=random.Random(2))
        game = self.make_game(companion)
        self.fill(game)
        game.grid.set_dot((0, 0), CompanionDot("blue"))
        game.grid.set_dot((0, 1), CompanionDot("blue"))
        self.connect(game)
        wildcards = [game.grid.dot_at(position)
                     for position in game.grid.positions()
                     if isinstance(game.grid.dot_at(position), WildcardDot)]
        self.assertEqual(len(wildcards), 2)

    def test_captain_companion_creates_beams_after_charging(self):
        companion = CaptainCompanion(charge_limit=2, beam_count=3,
                                     rng=random.Random(2))
        game = self.make_game(companion)
        self.fill(game, "purple")
        game.grid.set_dot((0, 0), CompanionDot("blue"))
        game.grid.set_dot((0, 1), CompanionDot("blue"))
        self.connect(game)
        beams = [game.grid.dot_at(position)
                 for position in game.grid.positions()
                 if isinstance(game.grid.dot_at(position), BeamDot)]
        self.assertEqual(len(beams), 3)
        self.assertTrue(all(beam.kind == "purple" for beam in beams))
        self.assertTrue(all(beam.direction in BeamDot.valid_directions
                            for beam in beams))

if __name__ == "__main__":
    unittest.main()
