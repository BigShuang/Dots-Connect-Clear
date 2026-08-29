"""Polymorphic dot types for Stage 2."""

from abc import ABC
from typing import Any, Optional, Set, Tuple

Position = Tuple[int, int]


class AbstractDot(ABC):
    """Common protocol used by the game, factory, and view."""

    asset_family = "basic"
    asset_variant: Optional[str] = None
    connectable = True

    def __init__(self, kind: str) -> None:
        self.kind = kind

    def can_connect(self, other: "AbstractDot") -> bool:
        return self.connectable and other.connectable and self.kind == other.kind

    def activate(self, grid: Any, position: Position) -> Set[Position]:
        """Return positions removed by this activation (one activation layer only)."""
        return {position}


class BasicDot(AbstractDot):
    """A regular coloured dot."""


class CompanionDot(BasicDot):
    """A basic dot which adds one charge when actually removed."""

    asset_family = "companion"


class StarDot(BasicDot):
    """Remove every dot matching this star's colour."""

    asset_family = "star"

    def activate(self, grid: Any, position: Position) -> Set[Position]:
        return set(grid.positions_of_kind(self.kind))


class FlowerDot(AbstractDot):
    """Remove itself and its orthogonal neighbours."""

    asset_family = "flower"

    def activate(self, grid: Any, position: Position) -> Set[Position]:
        return {position, *grid.neighbours(position)}


class SwirlDot(AbstractDot):
    """Recolour all eight surrounding dots, then remove itself."""

    asset_family = "swirl"

    def activate(self, grid: Any, position: Position) -> Set[Position]:
        row, column = position
        for other_position in grid.positions():
            other_row, other_column = other_position
            if other_position == position:
                continue
            if abs(other_row - row) <= 1 and abs(other_column - column) <= 1:
                current = grid.dot_at(other_position)
                if current is not None and current.connectable:
                    grid.set_dot(other_position, grid.factory.create_basic(self.kind))
        return {position}


class BeamDot(AbstractDot):
    asset_family = "beam"
    direction = "horizontal"

    @property
    def asset_variant(self) -> str:
        return self.direction


class HorizontalBeamDot(BeamDot):
    direction = "horizontal"

    def activate(self, grid: Any, position: Position) -> Set[Position]:
        row, _column = position
        return {(row, column) for column in range(grid.columns)}


class VerticalBeamDot(BeamDot):
    direction = "vertical"

    def activate(self, grid: Any, position: Position) -> Set[Position]:
        _row, column = position
        return {(row, column) for row in range(grid.rows)}


class CrossBeamDot(BeamDot):
    direction = "cross"

    def activate(self, grid: Any, position: Position) -> Set[Position]:
        row, column = position
        return ({(row, item) for item in range(grid.columns)} |
                {(item, column) for item in range(grid.rows)})


class WildcardDot(AbstractDot):
    """A connector which adopts the colour of the current connection."""

    asset_family = "wildcard"

    def __init__(self, kind: str = "wildcard") -> None:
        super().__init__(kind)

    def can_connect(self, other: AbstractDot) -> bool:
        return self.connectable and other.connectable


class DurableDot(AbstractDot):
    """A non-connectable obstacle which keeps mutable hit state."""

    connectable = False
    max_hits = 2

    def __init__(self, kind: str, hits_remaining: Optional[int] = None) -> None:
        super().__init__(kind)
        self.hits_remaining = self.max_hits if hits_remaining is None else hits_remaining

    def take_hit(self) -> bool:
        self.hits_remaining -= 1
        return self.hits_remaining <= 0


class TurtleDot(DurableDot):
    """Hide in its shell after one range hit, then disappear after another."""

    @property
    def asset_family(self) -> str:
        return "turtle" if self.hits_remaining >= self.max_hits else "shell"


class ShellDot(TurtleDot):
    """A turtle which starts hidden and therefore needs only one more hit."""

    def __init__(self, kind: str) -> None:
        super().__init__(kind, hits_remaining=1)


class AnchorDot(AbstractDot):
    """A non-connectable objective collected after falling to a segment bottom."""

    asset_family = "anchor"
    connectable = False
