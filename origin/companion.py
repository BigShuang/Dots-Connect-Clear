"""Companions and their board-changing abilities."""

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass
import random
from typing import TYPE_CHECKING, Iterable

from cell import Position

if TYPE_CHECKING:
    from game import DotGrid


@dataclass(slots=True)
class AbstractCompanion(ABC):
    """Chargeable helper shared by all companion implementations."""

    charge_limit: int = 6
    charge: int = 0

    def add_charge(
        self,
        amount: int,
        grid: "DotGrid",
        excluded: Iterable[Position] = (),
    ) -> int:
        """Add charge, activate once per full bar, and return activation count."""
        activations = 0
        excluded_positions = frozenset(excluded)
        for _ in range(max(0, amount)):
            self.charge += 1
            if self.charge >= self.charge_limit:
                self.charge = 0
                self.activate(grid, excluded_positions)
                activations += 1
        return activations

    def reset(self) -> None:
        self.charge = 0

    @abstractmethod
    def activate(self, grid: "DotGrid", excluded: Iterable[Position] = ()) -> None:
        """Perform this companion's ability."""


class EskimoCompanion(AbstractCompanion):
    """Place a few randomly coloured swirl dots in playable cells."""

    def __init__(
        self,
        charge_limit: int = 6,
        swirl_count: int = 3,
        rng: random.Random | None = None,
    ) -> None:
        super().__init__(charge_limit=charge_limit)
        self.swirl_count = max(0, swirl_count)
        self.rng = rng or random.Random()

    def activate(self, grid: "DotGrid", excluded: Iterable[Position] = ()) -> None:
        excluded_positions = frozenset(excluded)
        available = [
            position
            for position in grid.positions()
            if not grid.is_blocked(position)
            and position not in excluded_positions
            and grid.dot_at(position) is not None
        ]
        count = min(self.swirl_count, len(available))
        for position in self.rng.sample(available, count):
            current = grid.dot_at(position)
            if current is not None:
                grid.set_dot(position, grid.factory.create_swirl(current.kind))
