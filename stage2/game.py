"""Stage 2 board model, special-dot effects, and companion charging."""

from collections import Counter
from dataclasses import dataclass
import random
from typing import Iterable, Iterator, List, Optional, Set

from cell import Cell, Position
from companion import AbstractCompanion, EskimoCompanion, GardenerCompanion
from dot import (
    AbstractDot, AnchorDot, BasicDot, CompanionDot, DurableDot, FlowerDot,
    HorizontalBeamDot, ShellDot, SwirlDot, VerticalBeamDot, WildcardDot,
)
from factory import DOT_KINDS, DotFactory
from util import EventEmitter


DEFAULT_OBJECTIVES = {
    "coral": 25,
    "blue": 25,
    "purple": 15,
    "gold": 10,
}


# Choose the dots used by the GUI here. Keep only 2-3 types.
# The second number is the relative chance of creating that type.
ENABLED_DOT_TYPES = [
    (BasicDot, 88),
    (FlowerDot, 12),
]

# Use None for no companion, EskimoCompanion, or GardenerCompanion.
# When a companion is used, include CompanionDot above so it can charge.
COMPANION_TYPE = None

# Recommended combinations (copy one list into ENABLED_DOT_TYPES):
# Beam:     [(BasicDot, 82), (HorizontalBeamDot, 9), (VerticalBeamDot, 9)]
# Colour:   [(BasicDot, 80), (SwirlDot, 10), (WildcardDot, 10)]
# Eskimo:   [(BasicDot, 82), (CompanionDot, 18)]
# Gardener: [(BasicDot, 76), (CompanionDot, 16), (FlowerDot, 8)]
# Shell:    [(BasicDot, 80), (FlowerDot, 12), (ShellDot, 8)]
# Anchor:   [(BasicDot, 82), (HorizontalBeamDot, 10), (AnchorDot, 8)]


@dataclass(frozen=True)
class MoveResult:
    removed: int
    kind: str
    loop: bool
    score_gained: int


class DotGrid:
    """A rectangular board that owns cells and applies gravity."""

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
        self.blocked_positions = frozenset(blocked_positions)

        for position in self.blocked_positions:
            if not self.in_bounds(position):
                raise ValueError("Blocked positions must be inside the grid")

        self._cells: List[List[Cell]] = []
        for row in range(rows):
            grid_row: List[Cell] = []
            for column in range(columns):
                blocked = (row, column) in self.blocked_positions
                dot = None if blocked else self.factory.create_dot()
                grid_row.append(Cell(row, column, dot, blocked))
            self._cells.append(grid_row)
        self.ensure_playable()

    def in_bounds(self, position: Position) -> bool:
        row, column = position
        return 0 <= row < self.rows and 0 <= column < self.columns

    def cell_at(self, position: Position) -> Cell:
        if not self.in_bounds(position):
            raise IndexError("Position outside grid: " + str(position))
        row, column = position
        return self._cells[row][column]

    def dot_at(self, position: Position) -> Optional[AbstractDot]:
        return self.cell_at(position).dot

    def set_dot(self, position: Position, dot: Optional[AbstractDot]) -> None:
        cell = self.cell_at(position)
        if cell.blocked and dot is not None:
            raise ValueError("Cannot place a dot in a blocked cell")
        cell.dot = dot

    def positions(self) -> Iterator[Position]:
        for row in range(self.rows):
            for column in range(self.columns):
                yield row, column

    def positions_of_kind(self, kind: str) -> List[Position]:
        matching: List[Position] = []
        for position in self.positions():
            dot = self.dot_at(position)
            if dot is not None and dot.kind == kind:
                matching.append(position)
        return matching

    def neighbours(self, position: Position) -> List[Position]:
        row, column = position
        candidates = [
            (row - 1, column),
            (row + 1, column),
            (row, column - 1),
            (row, column + 1),
        ]
        return [candidate for candidate in candidates if self.in_bounds(candidate)]

    def is_blocked(self, position: Position) -> bool:
        return self.cell_at(position).blocked

    def remove(self, positions: Iterable[Position]) -> None:
        for position in set(positions):
            self.set_dot(position, None)

    def fall(self) -> None:
        """Move dots down within each segment separated by blocked cells."""
        for column in range(self.columns):
            for rows in self._open_segments(column):
                dots = []
                for row in rows:
                    dot = self._cells[row][column].dot
                    if dot is not None:
                        dots.append(dot)
                new_values = [None] * (len(rows) - len(dots)) + dots
                for row, dot in zip(rows, new_values):
                    self._cells[row][column].dot = dot

    def fill(self) -> None:
        for position in self.positions():
            cell = self.cell_at(position)
            if not cell.blocked and cell.is_empty():
                cell.dot = self.factory.create_dot()
        self.ensure_playable()

    def _open_segments(self, column: int) -> List[List[int]]:
        segments: List[List[int]] = []
        current: List[int] = []
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
        for position in self.positions():
            dot = self.dot_at(position)
            if dot is None:
                continue
            for neighbour in self.neighbours(position):
                other = self.dot_at(neighbour)
                if (other is not None and
                        (dot.can_connect(other) or other.can_connect(dot))):
                    return True
        return False

    def ensure_playable(self) -> None:
        """Guarantee that random generation leaves at least one legal pair."""
        if self.has_available_connection():
            return
        playable = [
            position
            for position in self.positions()
            if position not in self.blocked_positions
        ]
        for first in playable:
            for second in self.neighbours(first):
                if second not in self.blocked_positions:
                    kind = self.factory.rng.choice(self.factory.kinds)
                    self.set_dot(first, self.factory.create_basic(kind))
                    self.set_dot(second, self.factory.create_basic(kind))
                    return

    def kinds(self) -> List[List[Optional[str]]]:
        snapshot: List[List[Optional[str]]] = []
        for row in range(self.rows):
            values: List[Optional[str]] = []
            for column in range(self.columns):
                dot = self._cells[row][column].dot
                values.append(None if dot is None else dot.kind)
            snapshot.append(values)
        return snapshot


class DotGame(EventEmitter):
    """Game state and rules, independent of Tkinter."""

    def __init__(
        self,
        rows: int = 8,
        columns: int = 8,
        moves: int = 20,
        objectives: Optional[dict] = None,
        rng: Optional[random.Random] = None,
        blocked_positions: Optional[Iterable[Position]] = None,
        factory: Optional[DotFactory] = None,
        companion: Optional[AbstractCompanion] = None,
        with_companion: Optional[bool] = None,
    ) -> None:
        super().__init__()
        self.rows = rows
        self.columns = columns
        self.starting_moves = moves
        self.starting_objectives = dict(objectives or DEFAULT_OBJECTIVES)
        self.rng = rng if rng is not None else random.Random()
        self.factory = (
            factory if factory is not None
            else DotFactory(rng=self.rng, enabled_dot_types=ENABLED_DOT_TYPES)
        )
        if companion is not None:
            self.companion = companion
        elif with_companion is True:
            self.companion = EskimoCompanion(rng=self.rng)
        elif with_companion is False or COMPANION_TYPE is None:
            self.companion = None
        else:
            self.companion = COMPANION_TYPE(rng=self.rng)
        self.blocked_positions = frozenset(
            self.default_blocked_positions(rows, columns)
            if blocked_positions is None
            else blocked_positions
        )

        self.grid = DotGrid(rows, columns, self.factory, self.blocked_positions)
        self.score = 0
        self.moves_remaining = moves
        self.objectives = dict(self.starting_objectives)
        self.selection: List[Position] = []
        self.selection_kind: Optional[str] = None
        self.selection_has_loop = False
        self.resolving = False
        self.anchors_collected = 0

    @staticmethod
    def are_adjacent(first: Position, second: Position) -> bool:
        row_distance = abs(first[0] - second[0])
        column_distance = abs(first[1] - second[1])
        return row_distance + column_distance == 1

    @staticmethod
    def default_blocked_positions(rows: int, columns: int) -> Set[Position]:
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
        return all(amount == 0 for amount in self.objectives.values())

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
        self.resolving = False
        self.anchors_collected = 0
        if self.companion is not None:
            self.companion.reset()
        self.emit("reset")
        self.emit(
            "companion_changed",
            self.companion.charge if self.companion is not None else 0,
            0,
        )

    def start_selection(self, position: Position) -> bool:
        if self.is_over or self.resolving or not self.grid.in_bounds(position):
            return False
        dot = self.grid.dot_at(position)
        if dot is None or not dot.connectable:
            return False
        self.selection = [position]
        self.selection_kind = None if isinstance(dot, WildcardDot) else dot.kind
        self.selection_has_loop = False
        self.emit("selection_changed")
        return True

    def extend_selection(self, position: Position) -> bool:
        if self.resolving or not self.selection or not self.grid.in_bounds(position):
            return False
        previous = self.selection[-1]
        if position == previous:
            return False

        if len(self.selection) >= 2 and position == self.selection[-2]:
            self.selection.pop()
            self.selection_has_loop = len(self.selection) != len(set(self.selection))
            self._refresh_selection_kind()
            self.emit("selection_changed")
            return True

        if not self.are_adjacent(previous, position):
            return False
        dot = self.grid.dot_at(position)
        if dot is None or not dot.connectable:
            return False
        if not isinstance(dot, WildcardDot):
            if self.selection_kind is not None and dot.kind != self.selection_kind:
                return False
            if self.selection_kind is None:
                self.selection_kind = dot.kind
        previous_dot = self.grid.dot_at(previous)
        if previous_dot is None or not (
            previous_dot.can_connect(dot) or dot.can_connect(previous_dot)
        ):
            return False

        if position in self.selection:
            old_index = self.selection.index(position)
            if len(self.selection) - old_index < 4:
                return False
            self.selection_has_loop = True
        self.selection.append(position)
        self.emit("selection_changed")
        return True

    def finish_selection(self) -> Optional[MoveResult]:
        unique_positions = set(self.selection)
        if len(unique_positions) < 2:
            self.cancel_selection()
            return None

        self.resolving = True
        kind = self.selection_kind or "wildcard"
        loop = self.selection_has_loop
        removed_positions = (
            (self.grid.positions_of_kind(kind) + [
                position for position in self.grid.positions()
                if isinstance(self.grid.dot_at(position), WildcardDot)
            ]) if loop and self.selection_kind is not None else list(unique_positions)
        )
        activated_positions: Set[Position] = set(removed_positions)
        for position in removed_positions:
            dot = self.grid.dot_at(position)
            if dot is not None:
                activated_positions.update(dot.activate(self.grid, position))

        # Obstacles take damage instead of being blindly removed by a range effect.
        final_positions: Set[Position] = set()
        for position in activated_positions:
            if not self.grid.in_bounds(position) or self.grid.is_blocked(position):
                continue
            target = self.grid.dot_at(position)
            if isinstance(target, DurableDot):
                if target.take_hit():
                    final_positions.add(position)
            elif target is not None:
                final_positions.add(position)
        activated_positions = final_positions

        removed_counts = Counter()
        companion_dots = 0
        for position in activated_positions:
            dot = self.grid.dot_at(position)
            if dot is not None:
                removed_counts[dot.kind] += 1
                companion_dots += isinstance(dot, CompanionDot)

        activations = 0
        if self.companion is not None:
            activations = self.companion.add_charge(
                companion_dots, self.grid, activated_positions
            )
        if companion_dots and self.companion is not None:
            self.emit("companion_changed", self.companion.charge, activations)

        self._clear_selection()
        self.emit("selection_changed")
        self.emit("activate", tuple(activated_positions))
        self.grid.remove(activated_positions)
        self.emit("remove", tuple(activated_positions))
        self.grid.fall()
        self.emit("fall")
        self._collect_landed_anchors()
        self.grid.fill()
        self.emit("fill")

        self.moves_remaining -= 1
        score_gained = len(activated_positions) * 10
        self.score += score_gained
        for objective_kind, amount in removed_counts.items():
            if objective_kind in self.objectives:
                remaining = self.objectives[objective_kind] - amount
                self.objectives[objective_kind] = max(0, remaining)

        result = MoveResult(len(activated_positions), kind, loop, score_gained)
        self.resolving = False
        self.emit("move_completed", result)
        return result

    def cancel_selection(self) -> None:
        had_selection = bool(self.selection)
        self._clear_selection()
        if had_selection:
            self.emit("selection_changed")

    def _clear_selection(self) -> None:
        self.selection = []
        self.selection_kind = None
        self.selection_has_loop = False

    def _refresh_selection_kind(self) -> None:
        self.selection_kind = None
        for position in self.selection:
            dot = self.grid.dot_at(position)
            if dot is not None and not isinstance(dot, WildcardDot):
                self.selection_kind = dot.kind
                break

    def _collect_landed_anchors(self) -> None:
        """Collect anchors at the bottom of their gravity segment."""
        collected = []
        for position in self.grid.positions():
            if not isinstance(self.grid.dot_at(position), AnchorDot):
                continue
            row, column = position
            below = (row + 1, column)
            if row == self.grid.rows - 1 or self.grid.is_blocked(below):
                collected.append(position)
        if collected:
            self.grid.remove(collected)
            self.anchors_collected += len(collected)
            self.emit("anchors_collected", self.anchors_collected)
