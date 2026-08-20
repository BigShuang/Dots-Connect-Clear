"""Centralised construction of dots."""

import random
from typing import Optional, Sequence, Type

from dot import AbstractDot, BasicDot


DOT_KINDS = ("coral", "blue", "purple", "gold")


class DotFactory:
    """Create dots using an injectable random-number generator.

    ``dot_class`` deliberately defaults to BasicDot.  Stage 2 can supply a
    configured subclass or extend this factory without changing DotGrid.
    """

    def __init__(
        self,
        kinds: Sequence[str] = DOT_KINDS,
        rng: Optional[random.Random] = None,
        dot_class: Type[AbstractDot] = BasicDot,
    ) -> None:
        if not kinds:
            raise ValueError("At least one dot kind is required")
        self.kinds = tuple(kinds)
        self.rng = rng if rng is not None else random.Random()
        self.dot_class = dot_class

    def create_dot(self, kind: Optional[str] = None) -> AbstractDot:
        selected_kind = kind if kind is not None else self.rng.choice(self.kinds)
        if selected_kind not in self.kinds:
            raise ValueError("Unknown dot kind: " + selected_kind)
        return self.dot_class(selected_kind)

    def create_basic(self, kind: Optional[str] = None) -> BasicDot:
        """Compatibility-friendly explicit constructor for a basic dot."""
        selected_kind = kind if kind is not None else self.rng.choice(self.kinds)
        if selected_kind not in self.kinds:
            raise ValueError("Unknown dot kind: " + selected_kind)
        return BasicDot(selected_kind)
