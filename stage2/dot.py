"""Dot types.

Stage 1 uses only BasicDot.  The common parent class is already present so
Stage 2 can add new dot subclasses without changing DotGrid or GridView.
"""

from abc import ABC
from typing import Any, Set, Tuple


Position = Tuple[int, int]


class AbstractDot(ABC):
    """Common interface shared by every current and future dot type."""

    asset_family = "basic"

    def __init__(self, kind: str) -> None:
        self.kind = kind

    def can_connect(self, other: "AbstractDot") -> bool:
        """Return whether this dot may connect to *other*."""
        return self.kind == other.kind

    def activate(self, grid: Any, position: Position) -> Set[Position]:
        """Return positions affected when this dot is activated.

        Basic dots affect only themselves.  Stage 2 subclasses can override
        this method while DotGame keeps the same resolution flow.  ``grid``
        is intentionally supplied through this small public interface.
        """
        return {position}


class BasicDot(AbstractDot):
    """A regular coloured dot with no special activation effect."""

    pass
