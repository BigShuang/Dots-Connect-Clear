"""Chargeable helpers which demonstrate composition and polymorphism."""

from abc import ABC, abstractmethod
import random
from typing import Any, Iterable, Optional

from cell import Position
from dot import FlowerDot


class AbstractCompanion(ABC):
    def __init__(self, charge_limit: int = 6) -> None:
        if charge_limit <= 0:
            raise ValueError("charge_limit must be positive")
        self.charge_limit = charge_limit
        self.charge = 0

    def add_charge(self, amount: int, grid: Any,
                   excluded: Iterable[Position] = ()) -> int:
        activations = 0
        for _ in range(max(0, amount)):
            self.charge += 1
            if self.charge >= self.charge_limit:
                self.charge = 0
                self.activate(grid, excluded)
                activations += 1
        return activations

    def reset(self) -> None:
        self.charge = 0

    @abstractmethod
    def activate(self, grid: Any, excluded: Iterable[Position] = ()) -> None:
        pass


class EskimoCompanion(AbstractCompanion):
    """Turn several surviving dots into SwirlDots when fully charged."""

    def __init__(self, charge_limit: int = 6, swirl_count: int = 3,
                 rng: Optional[random.Random] = None) -> None:
        super().__init__(charge_limit)
        self.swirl_count = max(0, swirl_count)
        self.rng = rng if rng is not None else random.Random()

    def activate(self, grid: Any, excluded: Iterable[Position] = ()) -> None:
        excluded_set = set(excluded)
        available = [position for position in grid.positions()
                     if position not in excluded_set
                     and (dot := grid.dot_at(position)) is not None
                     and dot.connectable]
        for position in self.rng.sample(available, min(self.swirl_count, len(available))):
            current = grid.dot_at(position)
            grid.set_dot(position, grid.factory.create_swirl(current.kind))


class GardenerCompanion(AbstractCompanion):
    """A second interchangeable companion which plants one FlowerDot."""

    def __init__(self, charge_limit: int = 6,
                 rng: Optional[random.Random] = None) -> None:
        super().__init__(charge_limit)
        self.rng = rng if rng is not None else random.Random()

    def activate(self, grid: Any, excluded: Iterable[Position] = ()) -> None:
        excluded_set = set(excluded)
        available = [position for position in grid.positions()
                     if position not in excluded_set
                     and (dot := grid.dot_at(position)) is not None
                     and dot.connectable]
        if available:
            position = self.rng.choice(available)
            current = grid.dot_at(position)
            grid.set_dot(position, FlowerDot(current.kind))


class StarCompanion(AbstractCompanion):
    """Turn one surviving dot into a same-colour StarDot when charged."""

    def __init__(self, charge_limit: int = 6,
                 rng: Optional[random.Random] = None) -> None:
        super().__init__(charge_limit)
        self.rng = rng if rng is not None else random.Random()

    def activate(self, grid: Any, excluded: Iterable[Position] = ()) -> None:
        excluded_set = set(excluded)
        available = [position for position in grid.positions()
                     if position not in excluded_set
                     and (dot := grid.dot_at(position)) is not None
                     and dot.connectable]
        if available:
            position = self.rng.choice(available)
            current = grid.dot_at(position)
            grid.set_dot(position, grid.factory.create_star(current.kind))
