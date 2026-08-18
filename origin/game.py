"""Core model for Dots, companion abilities, and phased move resolution."""

from __future__ import annotations

from collections import Counter
from dataclasses import dataclass
import random
from typing import Iterable

from cell import Cell, Position
from companion import AbstractCompanion, EskimoCompanion
from dot import AbstractDot, CompanionDot, SwirlDot
from factory import DOT_KINDS, DotFactory
from util import EventEmitter


DEFAULT_OBJECTIVES = {
    "coral": 25,
    "blue": 25,
    "purple": 15,
    "gold": 10,
}


@dataclass(frozen=True, slots=True)
class MoveResult:
    removed: int
    kind: str
    loop: bool
    score_gained: int


@dataclass(slots=True)
class PendingMove:
    """Immutable-in-practice data carried through the four resolution phases."""

    positions: list[Position]
    kind: str
    loop: bool
    removed_counts: Counter[str]
    companion_dots: int = 0


class DotGrid:
    """Rectangular collection of cells with gravity-based refill."""

    def __init__(
        self,
        rows: int,
        columns: int,
        factory: DotFactory,
        blocked_positions: Iterable[Position] = (),
    ) -> None:
        if rows <= 0 or columns <= 0:
            raise ValueError("Grid dimensions must be positive")
        self.rows = rows
        self.columns = columns
        self.factory = factory
        blocked = set(blocked_positions)
        if any(not (0 <= row < rows and 0 <= column < columns) for row, column in blocked):
            raise ValueError("Blocked positions must be inside the grid")
        self.blocked_positions = frozenset(blocked)
        self._cells = [
            [
                Cell(
                    row,
                    column,
                    None if (row, column) in blocked else factory.create_basic(),
                    blocked=(row, column) in blocked,
                )
                for column in range(columns)
            ]
            for row in range(rows)
        ]
        self.ensure_playable()

    def in_bounds(self, position: Position) -> bool:
        row, column = position
        return 0 <= row < self.rows and 0 <= column < self.columns

    def cell_at(self, position: Position) -> Cell:
        if not self.in_bounds(position):
            raise IndexError(f"Position outside grid: {position}")
        row, column = position
        return self._cells[row][column]

    def dot_at(self, position: Position) -> AbstractDot | None:
        return self.cell_at(position).dot

    def set_dot(self, position: Position, dot: AbstractDot | None) -> None:
        cell = self.cell_at(position)
        if cell.blocked and dot is not None:
            raise ValueError(f"Cannot place a dot in blocked cell: {position}")
        cell.dot = dot

    def is_blocked(self, position: Position) -> bool:
        return self.cell_at(position).blocked

    def positions(self) -> Iterable[Position]:
        for row in range(self.rows):
            for column in range(self.columns):
                yield row, column

    def positions_of_kind(self, kind: str) -> list[Position]:
        return [
            position
            for position in self.positions()
            if (dot := self.dot_at(position)) is not None and dot.kind == kind
        ]

    def remove(self, positions: Iterable[Position]) -> None:
        for position in set(positions):
            self.set_dot(position, None)

    def fall(self) -> None:
        for column in range(self.columns):
            for segment in self._column_segments(column):
                surviving = [
                    self._cells[row][column].dot
                    for row in segment
                    if self._cells[row][column].dot is not None
                ]
                missing = len(segment) - len(surviving)
                column_dots = [None] * missing + surviving
                for row, dot in zip(segment, column_dots):
                    self._cells[row][column].dot = dot

    def fill(self) -> None:
        for position in self.positions():
            cell = self.cell_at(position)
            if not cell.blocked and cell.dot is None:
                cell.dot = self.factory.create_basic()
        self.ensure_playable()

    def remove_and_refill(self, positions: Iterable[Position]) -> None:
        """Compatibility helper which performs all three board phases."""
        self.remove(positions)
        self.fall()
        self.fill()

    def _column_segments(self, column: int) -> list[list[int]]:
        """Return contiguous playable row groups separated by blocked cells."""
        segments: list[list[int]] = []
        current: list[int] = []
        for row in range(self.rows):
            if self._cells[row][column].blocked:
                if current:
                    segments.append(current)
                    current = []
            else:
                current.append(row)
        if current:
            segments.append(current)
        return segments

    def has_available_connection(self) -> bool:
        """Return whether at least one orthogonally adjacent same-kind pair exists."""
        for row, column in self.positions():
            dot = self._cells[row][column].dot
            for neighbour in ((row + 1, column), (row, column + 1)):
                if self.in_bounds(neighbour):
                    other = self.dot_at(neighbour)
                    if dot is not None and other is not None and dot.can_connect(other):
                        return True
        return False

    def ensure_playable(self) -> None:
        """Guarantee a legal pair so a random refill cannot deadlock the board."""
        if self.rows * self.columns < 2 or self.has_available_connection():
            return
        first = self._cells[0][0].dot
        target = (0, 1) if self.columns > 1 else (1, 0)
        if first is not None:
            self.set_dot(target, self.factory.create_basic(first.kind))

    def kinds(self) -> list[list[str | None]]:
        """Return a serialisable snapshot useful in tests and debugging."""
        return [
            [
                self._cells[row][column].dot.kind
                if self._cells[row][column].dot is not None
                else None
                for column in range(self.columns)
            ]
            for row in range(self.rows)
        ]


class DotGame(EventEmitter):
    """Rules and state for a single game."""

    def __init__(
        self,
        rows: int = 8,
        columns: int = 8,
        moves: int = 20,
        objective_amount: int | None = None,
        rng: random.Random | None = None,
        blocked_positions: Iterable[Position] | None = None,
    ) -> None:
        super().__init__()
        self.rows = rows
        self.columns = columns
        self.starting_moves = moves
        self.starting_objectives = (
            dict(DEFAULT_OBJECTIVES)
            if objective_amount is None
            else {kind: objective_amount for kind in DOT_KINDS}
        )
        self.rng = rng or random.Random()
        self.factory = DotFactory(rng=self.rng)
        self.blocked_positions = frozenset(
            self._default_blocked_positions(rows, columns)
            if blocked_positions is None
            else blocked_positions
        )
        self.grid = DotGrid(rows, columns, self.factory, self.blocked_positions)
        self.score = 0
        self.moves_remaining = moves
        self.objectives = dict(self.starting_objectives)
        self.selection: list[Position] = []
        self.selection_kind: str | None = None
        self.selection_has_loop = False
        self._pending_move: PendingMove | None = None

    @staticmethod
    def are_adjacent(first: Position, second: Position) -> bool:
        return abs(first[0] - second[0]) + abs(first[1] - second[1]) == 1

    @staticmethod
    def _default_blocked_positions(rows: int, columns: int) -> set[Position]:
        if rows < 5 or columns < 5:
            return set()
        start_row = (rows - 3) // 2
        start_column = (columns - 3) // 2
        return {
            (row, column)
            for row in range(start_row, start_row + 3)
            for column in range(start_column, start_column + 3)
        }

    @property
    def won(self) -> bool:
        return all(remaining == 0 for remaining in self.objectives.values())

    @property
    def lost(self) -> bool:
        return self.moves_remaining == 0 and not self.won

    @property
    def is_over(self) -> bool:
        return self.won or self.lost

    def reset(self) -> None:
        self.grid = DotGrid(
            self.rows, self.columns, self.factory, self.blocked_positions
        )
        self.score = 0
        self.moves_remaining = self.starting_moves
        self.objectives = dict(self.starting_objectives)
        self.cancel_selection()
        self._pending_move = None
        self.emit("reset")

    def start_selection(self, position: Position) -> bool:
        if self.is_over or self.resolving or not self.grid.in_bounds(position):
            return False
        dot = self.grid.dot_at(position)
        if dot is None:
            return False
        self.selection = [position]
        self.selection_kind = dot.kind
        self.selection_has_loop = False
        self.emit("selection_changed")
        return True

    def extend_selection(self, position: Position) -> bool:
        if self.resolving or not self.selection or not self.grid.in_bounds(position):
            return False
        last = self.selection[-1]
        if position == last:
            return False

        if len(self.selection) >= 2 and position == self.selection[-2]:
            self.selection.pop()
            self.selection_has_loop = self._contains_loop()
            self.emit("selection_changed")
            return True

        if not self.are_adjacent(last, position):
            return False
        dot = self.grid.dot_at(position)
        if dot is None or dot.kind != self.selection_kind:
            return False

        if position in self.selection:
            previous_index = self.selection.index(position)
            if len(self.selection) - previous_index < 4:
                return False
            self.selection_has_loop = True
            self.selection.append(position)
        else:
            self.selection.append(position)
        self.emit("selection_changed")
        return True

    def finish_selection(self) -> MoveResult | None:
        """Resolve a move synchronously (useful for tests and non-GUI clients)."""
        pending = self.begin_resolution()
        if pending is None:
            return None
        self.activate_pending()
        self.remove_pending()
        self.fall_pending()
        return self.fill_pending()

    @property
    def resolving(self) -> bool:
        return self._pending_move is not None

    def begin_resolution(self) -> PendingMove | None:
        """Validate the selection and freeze everything needed by the move."""
        if self._pending_move is not None:
            return None
        unique_selection = set(self.selection)
        if len(unique_selection) < 2 or self.selection_kind is None:
            self.cancel_selection()
            return None

        kind = self.selection_kind
        loop = self.selection_has_loop
        removed_positions = (
            self.grid.positions_of_kind(kind) if loop else list(unique_selection)
        )
        removed_counts: Counter[str] = Counter(
            dot.kind
            for position in removed_positions
            if (dot := self.grid.dot_at(position)) is not None
        )
        companion_dots = sum(
            isinstance(self.grid.dot_at(position), CompanionDot)
            for position in removed_positions
        )
        self._pending_move = PendingMove(
            removed_positions, kind, loop, removed_counts, companion_dots
        )
        self._clear_selection()
        return self._pending_move

    def activate_pending(self) -> None:
        pending = self._require_pending()
        for position in pending.positions:
            dot = self.grid.dot_at(position)
            if isinstance(dot, SwirlDot):
                self._activate_swirl(position, dot.kind)
        self.emit("activate", tuple(pending.positions))

    def remove_pending(self) -> None:
        pending = self._require_pending()
        self.grid.remove(pending.positions)
        self.emit("remove", tuple(pending.positions))

    def fall_pending(self) -> None:
        self._require_pending()
        self.grid.fall()
        self.emit("fall")

    def fill_pending(self) -> MoveResult:
        pending = self._require_pending()
        self.grid.fill()
        self.moves_remaining -= 1
        score_gained = len(pending.positions) * 10
        self.score += score_gained
        for objective_kind, amount in pending.removed_counts.items():
            if objective_kind in self.objectives:
                self.objectives[objective_kind] = max(
                    0, self.objectives[objective_kind] - amount
                )
        result = MoveResult(
            len(pending.positions), pending.kind, pending.loop, score_gained
        )
        self._pending_move = None
        self.emit("fill")
        self.emit("move_completed", result)
        return result

    def abort_resolution(self) -> None:
        """Clear an in-flight move so clients can always recover their input lock."""
        self._pending_move = None
        self.cancel_selection()

    def _require_pending(self) -> PendingMove:
        if self._pending_move is None:
            raise RuntimeError("No move is being resolved")
        return self._pending_move

    def _activate_swirl(self, position: Position, kind: str) -> None:
        row, column = position
        for neighbour_row in range(row - 1, row + 2):
            for neighbour_column in range(column - 1, column + 2):
                neighbour = neighbour_row, neighbour_column
                if neighbour == position or not self.grid.in_bounds(neighbour):
                    continue
                current = self.grid.dot_at(neighbour)
                if current is not None:
                    self.grid.set_dot(neighbour, self.factory.create_basic(kind))

    def cancel_selection(self) -> None:
        had_selection = bool(self.selection)
        self._clear_selection()
        if had_selection:
            self.emit("selection_changed")

    def _clear_selection(self) -> None:
        self.selection = []
        self.selection_kind = None
        self.selection_has_loop = False

    def _contains_loop(self) -> bool:
        return len(self.selection) != len(set(self.selection))


class CompanionGame(DotGame):
    """A game whose companion dots charge an Eskimo companion."""

    def __init__(
        self,
        *args: object,
        companion: AbstractCompanion | None = None,
        companion_dot_chance: float = 0.18,
        **kwargs: object,
    ) -> None:
        self.companion = companion
        self.companion_dot_chance = max(0.0, min(1.0, companion_dot_chance))
        super().__init__(*args, **kwargs)
        self.factory.companion_chance = self.companion_dot_chance
        if self.companion is None:
            self.companion = EskimoCompanion(rng=self.rng)
        self._seed_companion_dots()

    def _seed_companion_dots(self) -> None:
        for position in self.grid.positions():
            dot = self.grid.dot_at(position)
            if dot is not None and self.rng.random() < self.companion_dot_chance:
                self.grid.set_dot(position, self.factory.create_companion(dot.kind))

    def activate_pending(self) -> None:
        pending = self._require_pending()
        for position in pending.positions:
            dot = self.grid.dot_at(position)
            if isinstance(dot, SwirlDot):
                self._activate_swirl(position, dot.kind)
        if self.companion is not None and pending.companion_dots:
            activations = self.companion.add_charge(
                pending.companion_dots, self.grid, pending.positions
            )
            self.emit("companion_changed", self.companion.charge, activations)
        self.emit("activate", tuple(pending.positions))

    def reset(self) -> None:
        super().reset()
        if self.companion is not None:
            self.companion.reset()
        self.emit("companion_changed", self.companion.charge if self.companion else 0, 0)
