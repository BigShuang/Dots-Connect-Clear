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

    # TODO 1.1：计算上、下、左、右四个位置，只加入棋盘范围内的位置。
    def activate(self, grid, position):
        row, column = position
        affected = {position}
        directions = [(-1, 0), (1, 0), (0, -1), (0, 1)]
        for row_change, column_change in directions:
            neighbour = (row + row_change, column + column_change)
            if grid.in_bounds(neighbour):
                affected.add(neighbour)
        return affected

class CompanionDot(BasicDot):
    """A basic dot which adds one charge when actually removed."""
    # For 2.1：设置 CompanionDot 对应的素材类别；无需重写 activate。
    asset_family = "companion"


class StarDot(BasicDot):
    """Remove every dot matching this star's colour."""
    asset_family = "star"
    # TODO 2.3：遍历棋盘，收集全部与 StarDot 同色的 Dot 位置。
    def activate(self, grid, position):
        affected = set()
        for other_position in grid.positions():
            dot = grid.dot_at(other_position)
            if dot is not None and dot.kind == self.kind:
                affected.add(other_position)
        return affected


class SwirlDot(AbstractDot):
    """Recolour all eight surrounding dots, then remove itself."""
    asset_family = "swirl"

    # TODO 3.1：遍历周围八格，将有效可连接 Dot 改成与 SwirlDot 相同的颜色。
    def activate(self, grid, position):
        row, column = position
        for row_change in (-1, 0, 1):
            for column_change in (-1, 0, 1):
                if row_change == 0 and column_change == 0:
                    continue
                other_position = (row + row_change, column + column_change)
                if not grid.in_bounds(other_position):
                    continue
                dot = grid.dot_at(other_position)
                if dot is not None and dot.connectable:
                    dot.kind = self.kind
        return {position}


class BeamDot(AbstractDot):
    """A beam whose direction determines whether it affects a row, column, or both."""

    asset_family = "beam"
    valid_directions = ("horizontal", "vertical", "cross")

    # TODO 4.1：保存方向，并根据方向返回整行、整列或两者并集。
    def __init__(self, kind, direction):
        super().__init__(kind)
        if direction not in self.valid_directions:
            raise ValueError("Unknown beam direction: " + direction)
        self.direction = direction
        self.asset_variant = direction

    def activate(self, grid, position):
        row, column = position
        affected = set()
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

    # For Extension：Wildcard 的构造和连接规则已经提供。
    def __init__(self, kind: str = "wildcard") -> None:
        super().__init__(kind)

    def can_connect(self, other: AbstractDot) -> bool:
        return self.connectable and other.connectable


class TurtleDot(AbstractDot):
    """Hide in its shell after one range hit, then disappear after another."""

    connectable = False

    # TODO 5.1：保存两点耐久；第一次命中变成 shell，第二次命中后返回 True。
    def __init__(self, kind, hits_remaining=2):
        super().__init__(kind)
        self.hits_remaining = hits_remaining
        self.asset_family = "turtle" if hits_remaining == 2 else "shell"

    def take_hit(self):
        self.hits_remaining -= 1
        if self.hits_remaining == 1:
            self.asset_family = "shell"
            return False
        return True


class ShellDot(TurtleDot):
    """A turtle which starts hidden and therefore needs only one more hit."""

    # For 5.1：ShellDot 复用 TurtleDot，但从一点剩余耐久开始。
    def __init__(self, kind: str) -> None:
        super().__init__(kind, hits_remaining=1)


class AnchorDot(AbstractDot):
    """A non-connectable objective collected after falling to a segment bottom."""

    asset_family = "anchor"
    connectable = False

    # TODO Extension 5.2：判断 Anchor 下方是否还存在可玩的棋盘位置。
    def has_landed(self, grid, position):
        row, column = position
        for next_row in range(row + 1, grid.rows):
            if not grid.is_blocked((next_row, column)):
                return False
        return True
