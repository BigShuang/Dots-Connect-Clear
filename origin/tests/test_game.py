from __future__ import annotations

import random
import sys
from pathlib import Path
import unittest


SRC = Path(__file__).resolve().parents[1]
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from companion import EskimoCompanion
from dot import BasicDot, CompanionDot, SwirlDot
from game import CompanionGame, DotGame


class DotGameTest(unittest.TestCase):
    def make_game(self) -> DotGame:
        return DotGame(rows=3, columns=3, moves=3, objective_amount=2, rng=random.Random(7))

    @staticmethod
    def set_kinds(game: DotGame, rows: list[list[str]]) -> None:
        for row, values in enumerate(rows):
            for column, kind in enumerate(values):
                game.grid.set_dot((row, column), BasicDot(kind))

    def test_orthogonal_adjacency_only(self) -> None:
        self.assertTrue(DotGame.are_adjacent((0, 0), (0, 1)))
        self.assertTrue(DotGame.are_adjacent((1, 1), (2, 1)))
        self.assertFalse(DotGame.are_adjacent((0, 0), (1, 1)))
        self.assertFalse(DotGame.are_adjacent((0, 0), (0, 2)))

    def test_default_board_is_eight_by_eight_with_central_three_by_three_block(self) -> None:
        game = DotGame(rng=random.Random(7))
        self.assertEqual((game.rows, game.columns), (8, 8))
        self.assertEqual(len(game.grid.blocked_positions), 9)
        self.assertEqual(
            game.grid.blocked_positions,
            {(row, column) for row in range(2, 5) for column in range(2, 5)},
        )
        self.assertTrue(
            all(game.grid.dot_at(position) is None for position in game.grid.blocked_positions)
        )

    def test_connection_removes_dots_updates_score_and_move(self) -> None:
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
        self.assertEqual(len(game.grid.kinds()), 3)
        self.assertTrue(all(len(row) == 3 for row in game.grid.kinds()))

    def test_invalid_single_dot_does_not_consume_move(self) -> None:
        game = self.make_game()
        game.start_selection((0, 0))
        self.assertIsNone(game.finish_selection())
        self.assertEqual(game.moves_remaining, 3)
        self.assertEqual(game.score, 0)

    def test_backtracking_removes_last_selected_position(self) -> None:
        game = self.make_game()
        self.set_kinds(game, [["blue"] * 3 for _ in range(3)])
        game.start_selection((0, 0))
        game.extend_selection((0, 1))
        game.extend_selection((0, 2))
        self.assertTrue(game.extend_selection((0, 1)))
        self.assertEqual(game.selection, [(0, 0), (0, 1)])

    def test_loop_removes_every_dot_of_selected_kind(self) -> None:
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
        self.assertEqual(game.score, 50)

    def test_reset_restores_initial_state(self) -> None:
        game = self.make_game()
        game.score = 100
        game.moves_remaining = 0
        game.objectives["coral"] = 0
        game.reset()
        self.assertEqual(game.score, 0)
        self.assertEqual(game.moves_remaining, 3)
        self.assertEqual(game.objectives["coral"], 2)
        self.assertFalse(game.selection)

    def test_board_always_has_an_available_connection(self) -> None:
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

    def test_resolution_exposes_four_ordered_phases(self) -> None:
        game = self.make_game()
        self.set_kinds(game, [["blue"] * 3 for _ in range(3)])
        events: list[str] = []
        for event in ("activate", "remove", "fall", "fill"):
            game.on(event, lambda *_args, event=event: events.append(event))
        game.start_selection((0, 0))
        game.extend_selection((0, 1))
        self.assertIsNotNone(game.begin_resolution())
        self.assertTrue(game.resolving)
        self.assertFalse(game.start_selection((1, 0)))
        game.activate_pending()
        game.remove_pending()
        self.assertIsNone(game.grid.dot_at((0, 0)))
        game.fall_pending()
        game.fill_pending()
        self.assertEqual(events, ["activate", "remove", "fall", "fill"])
        self.assertFalse(game.resolving)
        self.assertEqual(game.moves_remaining, 2)

    def test_swirl_recolours_all_valid_neighbours_during_activation(self) -> None:
        game = self.make_game()
        self.set_kinds(game, [["blue"] * 3 for _ in range(3)])
        game.grid.set_dot((1, 1), SwirlDot("coral"))
        game.grid.set_dot((1, 2), BasicDot("coral"))
        game.start_selection((1, 1))
        game.extend_selection((1, 2))
        game.begin_resolution()
        game.activate_pending()
        self.assertEqual(game.grid.dot_at((0, 0)).kind, "coral")
        self.assertEqual(game.grid.dot_at((2, 2)).kind, "coral")

    def test_companion_dots_charge_and_activate_eskimo(self) -> None:
        companion = EskimoCompanion(
            charge_limit=2, swirl_count=2, rng=random.Random(11)
        )
        game = CompanionGame(
            rows=3,
            columns=3,
            moves=3,
            objective_amount=9,
            rng=random.Random(7),
            companion=companion,
            companion_dot_chance=0,
        )
        self.set_kinds(game, [["blue"] * 3 for _ in range(3)])
        game.grid.set_dot((0, 0), CompanionDot("blue"))
        game.grid.set_dot((0, 1), CompanionDot("blue"))
        game.start_selection((0, 0))
        game.extend_selection((0, 1))
        game.begin_resolution()
        game.activate_pending()
        self.assertEqual(companion.charge, 0)
        swirls = sum(
            isinstance(game.grid.dot_at(position), SwirlDot)
            for position in game.grid.positions()
        )
        self.assertEqual(swirls, 2)


if __name__ == "__main__":
    unittest.main()
