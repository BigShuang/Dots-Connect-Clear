"""Dot model types.

Only BasicDot is required for the stage 0-5 playable version.  Later stages can
extend AbstractDot without changing DotGrid or the Tkinter views.
"""

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

