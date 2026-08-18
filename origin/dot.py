"""Dot model types used by the basic and companion games."""

from __future__ import annotations

from abc import ABC
from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class AbstractDot(ABC):
    """Common interface shared by every dot type."""

    kind: str

    def can_connect(self, other: "AbstractDot") -> bool:
        return self.kind == other.kind


@dataclass(frozen=True, slots=True)
class BasicDot(AbstractDot):
    """A regular coloured dot with no special activation effect."""


@dataclass(frozen=True, slots=True)
class CompanionDot(BasicDot):
    """A selectable dot which charges the active companion when removed."""


@dataclass(frozen=True, slots=True)
class SwirlDot(AbstractDot):
    """A dot which recolours all eight neighbouring dots when activated."""
