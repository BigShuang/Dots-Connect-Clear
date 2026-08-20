"""Central, weighted registration and construction of Stage 2 dots."""

import random
from typing import Optional, Sequence, Tuple, Type

from dot import (
    AbstractDot, AnchorDot, BasicDot, CompanionDot, CrossBeamDot, FlowerDot,
    HorizontalBeamDot, ShellDot, SwirlDot, TurtleDot, VerticalBeamDot, WildcardDot,
)

DOT_KINDS = ("coral", "blue", "purple", "gold")
DotRegistration = Tuple[Type[AbstractDot], int]
DEFAULT_DOT_TYPES: Tuple[DotRegistration, ...] = (
    (BasicDot, 72), (CompanionDot, 10), (FlowerDot, 5), (SwirlDot, 4),
    (HorizontalBeamDot, 3), (VerticalBeamDot, 3), (CrossBeamDot, 1),
    (WildcardDot, 2),
)


class DotFactory:
    """Create a configurable mixture of dot subclasses using one RNG."""

    def __init__(self, kinds: Sequence[str] = DOT_KINDS,
                 rng: Optional[random.Random] = None,
                 dot_class: Optional[Type[AbstractDot]] = None,
                 enabled_dot_types: Optional[Sequence[DotRegistration]] = None) -> None:
        if not kinds:
            raise ValueError("At least one dot kind is required")
        self.kinds = tuple(kinds)
        self.rng = rng if rng is not None else random.Random()
        registrations = (((dot_class, 1),) if dot_class is not None
                         else tuple(enabled_dot_types or DEFAULT_DOT_TYPES))
        if not registrations or any(weight <= 0 for _dot_type, weight in registrations):
            raise ValueError("Dot registrations need positive weights")
        self.enabled_dot_types = registrations

    def _kind(self, kind: Optional[str]) -> str:
        selected = kind if kind is not None else self.rng.choice(self.kinds)
        if selected not in self.kinds:
            raise ValueError("Unknown dot kind: " + selected)
        return selected

    def create_dot(self, kind: Optional[str] = None) -> AbstractDot:
        types = [dot_type for dot_type, _weight in self.enabled_dot_types]
        weights = [weight for _dot_type, weight in self.enabled_dot_types]
        dot_type = self.rng.choices(types, weights=weights, k=1)[0]
        return WildcardDot() if dot_type is WildcardDot else dot_type(self._kind(kind))

    def create_basic(self, kind: Optional[str] = None) -> BasicDot:
        return BasicDot(self._kind(kind))

    def create_special(self, dot_type: Type[AbstractDot],
                       kind: Optional[str] = None) -> AbstractDot:
        return WildcardDot() if dot_type is WildcardDot else dot_type(self._kind(kind))

    def create_companion(self, kind: Optional[str] = None) -> CompanionDot:
        return CompanionDot(self._kind(kind))

    def create_swirl(self, kind: Optional[str] = None) -> SwirlDot:
        return SwirlDot(self._kind(kind))


CHALLENGE_DOT_TYPES = (ShellDot, TurtleDot, AnchorDot)
