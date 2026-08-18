"""Factories for constructing dots."""

from __future__ import annotations

import random
from collections.abc import Sequence

from dot import BasicDot, CompanionDot, SwirlDot


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
        self.companion_chance = 0.0

    def create_basic(self, kind: str | None = None) -> BasicDot:
        selected_kind = kind if kind is not None else self.rng.choice(self.kinds)
        if selected_kind not in self.kinds:
            raise ValueError(f"Unknown dot kind: {selected_kind}")
        if kind is None and self.rng.random() < self.companion_chance:
            return CompanionDot(selected_kind)
        return BasicDot(selected_kind)

    def create_companion(self, kind: str | None = None) -> CompanionDot:
        return CompanionDot(self._validated_kind(kind))

    def create_swirl(self, kind: str | None = None) -> SwirlDot:
        return SwirlDot(self._validated_kind(kind))

    def _validated_kind(self, kind: str | None) -> str:
        selected_kind = kind if kind is not None else self.rng.choice(self.kinds)
        if selected_kind not in self.kinds:
            raise ValueError(f"Unknown dot kind: {selected_kind}")
        return selected_kind
