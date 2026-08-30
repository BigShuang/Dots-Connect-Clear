"""Central, weighted registration and construction of Stage 2 dots."""

import random
from typing import Optional, Sequence, Tuple, Type

from dot import (
    AbstractDot, AnchorDot, BasicDot, BeamDot, CompanionDot, FlowerDot,
    ShellDot, StarDot, SwirlDot, TurtleDot, WildcardDot,
)

DOT_KINDS = ("coral", "blue", "purple", "gold")
DotRegistration = Tuple[Type[AbstractDot], int]
DEFAULT_DOT_TYPES: Tuple[DotRegistration, ...] = (
    (BasicDot, 72), (CompanionDot, 10), (FlowerDot, 5), (SwirlDot, 4),
    (BeamDot, 7), (WildcardDot, 2),
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

    def create_dot(self, kind: Optional[str] = None,
                   dot_type: Optional[Type[AbstractDot]] = None,
                   direction: Optional[str] = None) -> AbstractDot:
        # 未指定类型时，按 config 中的相对权重选择一个 Dot 类。
        if dot_type is None:
            types = [item for item, _weight in self.enabled_dot_types]
            weights = [weight for _item, weight in self.enabled_dot_types]
            dot_type = self.rng.choices(types, weights=weights, k=1)[0]

        # For Extension 4.1：Wildcard 没有普通颜色，使用自己的默认 kind。
        if dot_type is WildcardDot:
            return WildcardDot()

        # For 3.1：Beam 的方向由调用者传入，或由 Factory 的 RNG 选择。
        if dot_type is BeamDot:
            selected_direction = (
                self.rng.choice(BeamDot.valid_directions)
                if direction is None else direction
            )
            return BeamDot(self._kind(kind), selected_direction)

        return dot_type(self._kind(kind))


CHALLENGE_DOT_TYPES = (TurtleDot, ShellDot, AnchorDot)
