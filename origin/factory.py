"""Factories for constructing dots."""

from __future__ import annotations

import random
from collections.abc import Sequence

from dot import BasicDot


DOT_KINDS = ("coral", "blue", "purple", "gold")

class DotFactory:
    """Create basic dots using an injectable random generator."""

    def __init__(
        self,
        kinds: Sequence[str] = DOT_KINDS,
        rng: random.Random | None = None,
    ) -> None:
        if not kinds:
            raise ValueError("At least one dot kind is required")
        self.kinds = tuple(kinds)
        self.rng = rng or random.Random()

    def create_basic(self, kind: str | None = None) -> BasicDot:
        selected_kind = kind if kind is not None else self.rng.choice(self.kinds)
        if selected_kind not in self.kinds:
            raise ValueError(f"Unknown dot kind: {selected_kind}")
        return BasicDot(selected_kind)
