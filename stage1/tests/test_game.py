import random
import sys
from pathlib import Path
import unittest


STAGE1 = Path(__file__).resolve().parents[1]
if str(STAGE1) not in sys.path:
    sys.path.insert(0, str(STAGE1))

from dot import BasicDot
from game import DotGame


class DotGameTest(unittest.TestCase):
    def make_game(self) -> DotGame:
        objectives = {"coral": 2, "blue": 2, "purple": 2, "gold": 2}
        return DotGame(
            rows=3,
            columns=3,
            moves=3,
            objectives=objectives,
            rng=random.Random(7),
        )

    @staticmethod
    def set_kinds(game: DotGame, values: list[list[str]]) -> None:
        for row, row_values in enumerate(values):
            for column, kind in enumerate(row_values):
                game.grid.set_dot((row, column), BasicDot(kind))

    def test_only_orthogonal_positions_are_adjacent(self) -> None:
        self.assertTrue(DotGame.are_adjacent((0, 0), (0, 1)))
        self.assertTrue(DotGame.are_adjacent((1, 1), (2, 1)))
        self.assertFalse(DotGame.are_adjacent((0, 0), (1, 1)))
        self.assertFalse(DotGame.are_adjacent((0, 0), (0, 2)))

    def test_default_board_has_central_three_by_three_block(self) -> None:
        game = DotGame(rng=random.Random(4))
        expected = {(row, column) for row in range(2, 5) for column in range(2, 5)}
        self.assertEqual(game.grid.blocked_positions, expected)
        self.assertTrue(all(game.grid.dot_at(position) is None for position in expected))

    def test_connection_updates_board_score_moves_and_objective(self) -> None:
        game = self.make_game()
        self.set_kinds(
            game,
            [
                ["coral", "coral", "blue"],
                ["purple", "gold", "blue"],
                ["purple", "gold", "coral"],
            ],
        )
        self.assertTrue(game.start_selection((0, 0)))
        self.assertTrue(game.extend_selection((0, 1)))
        result = game.finish_selection()
        self.assertIsNotNone(result)
        self.assertEqual(result.removed, 2)
        self.assertEqual(game.score, 20)
        self.assertEqual(game.moves_remaining, 2)
        self.assertEqual(game.objectives["coral"], 0)
        self.assertTrue(
            all(game.grid.dot_at(position) is not None for position in game.grid.positions())
        )

    def test_single_dot_does_not_consume_move(self) -> None:
        game = self.make_game()
        game.start_selection((0, 0))
        self.assertIsNone(game.finish_selection())
        self.assertEqual(game.moves_remaining, 3)
        self.assertEqual(game.score, 0)

    def test_dragging_back_one_position_backtracks(self) -> None:
        game = self.make_game()
        self.set_kinds(game, [["blue"] * 3 for _ in range(3)])
        game.start_selection((0, 0))
        game.extend_selection((0, 1))
        game.extend_selection((0, 2))
        self.assertTrue(game.extend_selection((0, 1)))
        self.assertEqual(game.selection, [(0, 0), (0, 1)])

    def test_loop_removes_every_dot_of_the_selected_kind(self) -> None:
        game = self.make_game()
        self.set_kinds(
            game,
            [
                ["coral", "coral", "blue"],
                ["coral", "coral", "blue"],
                ["gold", "gold", "coral"],
            ],
        )
        game.start_selection((0, 0))
        for position in [(0, 1), (1, 1), (1, 0), (0, 0)]:
            self.assertTrue(game.extend_selection(position))
        result = game.finish_selection()
        self.assertTrue(result.loop)
        self.assertEqual(result.removed, 5)
        self.assertEqual(result.score_gained, 50)

    def test_reset_restores_initial_state(self) -> None:
        game = self.make_game()
        game.score = 100
        game.moves_remaining = 0
        game.objectives["coral"] = 0
        game.reset()
        self.assertEqual(game.score, 0)
        self.assertEqual(game.moves_remaining, 3)
        self.assertEqual(game.objectives["coral"], 2)
        self.assertEqual(game.selection, [])

    def test_grid_is_repaired_when_no_connection_exists(self) -> None:
        game = self.make_game()
        self.set_kinds(
            game,
            [
                ["coral", "blue", "coral"],
                ["blue", "coral", "blue"],
                ["coral", "blue", "coral"],
            ],
        )
        self.assertFalse(game.grid.has_available_connection())
        game.grid.ensure_playable()
        self.assertTrue(game.grid.has_available_connection())


if __name__ == "__main__":
    unittest.main()
