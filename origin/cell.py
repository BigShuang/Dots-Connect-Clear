"""Grid cell data structures."""

from __future__ import annotations

from dataclasses import dataclass

from dot import AbstractDot


Position = tuple[int, int]


@dataclass(slots=True)
class Cell:
    row: int
    column: int
    dot: AbstractDot | None = None
    blocked: bool = False

    @property
    def position(self) -> Position:
        return self.row, self.column
