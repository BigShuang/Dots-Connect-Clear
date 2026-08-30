"""Polymorphic dot types for Stage 2."""

from abc import ABC
from typing import Any, Optional, Set, Tuple

Position = Tuple[int, int]


class AbstractDot(ABC):
    """Common protocol used by the game, factory, and view."""

    asset_family = "basic"
    asset_variant: Optional[str] = None
    connectable = True

    def __init__(self, kind: str) -> None:
        self.kind = kind

    def can_connect(self, other: "AbstractDot") -> bool:
        return self.connectable and other.connectable and self.kind == other.kind

    def activate(self, grid: Any, position: Position) -> Set[Position]:
        """Return positions removed by this activation (one activation layer only)."""
        return {position}


class BasicDot(AbstractDot):
    """A regular coloured dot."""


class FlowerDot(AbstractDot):
    """Remove itself and its orthogonal neighbours."""
    # 指定使用花朵素材，即设置素材所在文件夹
    asset_family = "flower"

    # TODO 1.1：返回 FlowerDot 自身及上、下、左、右有效邻居的位置集合。
    def activate(self, grid: Any, position: Position) -> Set[Position]:
        affected = {position}
        affected.update(grid.neighbours(position))
        return affected

class CompanionDot(BasicDot):
    """A basic dot which adds one charge when actually removed."""
    # For 2.1：设置 CompanionDot 对应的素材类别；无需重写 activate。
    asset_family = "companion"


class StarDot(BasicDot):
    """Remove every dot matching this star's colour."""
    asset_family = "star"
    # TODO 2.2：返回棋盘上全部与 StarDot 同色的 Dot 位置。
    def activate(self, grid: Any, position: Position) -> Set[Position]:
        return set(grid.positions_of_kind(self.kind))


class SwirlDot(AbstractDot):
    """Recolour all eight surrounding dots, then remove itself."""
    asset_family = "swirl"

    # TODO 3.2：将周围八格内可连接的 Dot 改成同色 BasicDot，并只返回自身位置。
    def activate(self, grid: Any, position: Position) -> Set[Position]:
        row, column = position
        for other_position in grid.positions():
            other_row, other_column = other_position
            if other_position == position:
                continue
            if abs(other_row - row) <= 1 and abs(other_column - column) <= 1:
                current = grid.dot_at(other_position)
                if current is not None and current.connectable:
                    grid.set_dot(other_position, grid.factory.create_dot(
                        kind=self.kind, dot_type=BasicDot
                    ))
        return {position}


class BeamDot(AbstractDot):
    """A beam whose direction determines whether it affects a row, column, or both."""

    asset_family = "beam"
    valid_directions = ("horizontal", "vertical", "cross")

    # TODO 3.1：保存外部传入的合法方向，并根据方向返回整行、整列或两者并集。
    def __init__(self, kind: str, direction: str) -> None:
        super().__init__(kind)
        if direction not in self.valid_directions:
            raise ValueError("Unknown beam direction: " + direction)
        self.direction = direction

    @property
    def asset_variant(self) -> str:
        return self.direction

    def activate(self, grid: Any, position: Position) -> Set[Position]:
        row, column = position
        affected: Set[Position] = set()
        if self.direction in {"horizontal", "cross"}:
            for item in range(grid.columns):
                affected.add((row, item))
        if self.direction in {"vertical", "cross"}:
            for item in range(grid.rows):
                affected.add((item, column))
        return affected


class WildcardDot(AbstractDot):
    """A connector which adopts the colour of the current connection."""

    asset_family = "wildcard"

    # TODO Extension 4.1：使用默认 kind "wildcard"，并允许连接任意可连接 Dot。
    def __init__(self, kind: str = "wildcard") -> None:
        super().__init__(kind)

    def can_connect(self, other: AbstractDot) -> bool:
        return self.connectable and other.connectable


class DurableDot(AbstractDot):
    """A non-connectable obstacle which keeps mutable hit state."""

    # TODO Extension 4.2：设置为不可连接，保存剩余耐久，并在命中时判断是否移除。
    connectable = False
    max_hits = 2

    def __init__(self, kind: str, hits_remaining: Optional[int] = None) -> None:
        super().__init__(kind)
        if hits_remaining is None:
            self.hits_remaining = self.max_hits
        else:
            self.hits_remaining = hits_remaining

    def take_hit(self) -> bool:
        self.hits_remaining -= 1
        return self.hits_remaining <= 0


class TurtleDot(DurableDot):
    """Hide in its shell after one range hit, then disappear after another."""

    # TODO Extension 4.2：根据剩余耐久动态返回 turtle 或 shell 素材类别。
    @property
    def asset_family(self) -> str:
        if self.hits_remaining >= self.max_hits:
            return "turtle"
        return "shell"


class ShellDot(TurtleDot):
    """A turtle which starts hidden and therefore needs only one more hit."""

    # TODO Extension 4.2：让直接生成的 ShellDot 从 1 点剩余耐久开始。
    def __init__(self, kind: str) -> None:
        super().__init__(kind, hits_remaining=1)


class AnchorDot(AbstractDot):
    """A non-connectable objective collected after falling to a segment bottom."""

    # TODO Extension 4.3：设置 AnchorDot 的素材类别，并令其不可直接连接。
    asset_family = "anchor"
    connectable = False
