"""Small data objects used by the game grid."""

from dataclasses import dataclass
from typing import Optional, Tuple

from dot import AbstractDot


Position = Tuple[int, int]


@dataclass
class Cell:
    """One position on the board."""

    row: int
    column: int
    dot: Optional[AbstractDot] = None
    blocked: bool = False

    @property
    def position(self) -> Position:
        return self.row, self.column

    def is_empty(self) -> bool:
        return self.dot is None
