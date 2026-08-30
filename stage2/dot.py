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
        # 先把当前位置拆成行和列，后面才能分别修改两个坐标。
        row, column = position
        # Flower 自己一定会被移除，所以结果集合一开始就包含 position。
        affected = {position}
        # 每个 tuple 表示一次“行变化、列变化”，合起来正好是四个方向。
        directions = [(-1, 0), (1, 0), (0, -1), (0, 1)]
        for row_change, column_change in directions:
            neighbour = (row + row_change, column + column_change)
            # 角落和边缘的 Flower 会算出棋盘外坐标，必须先检查再加入。
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
        # 使用 set 保存匹配位置：同一个位置即使被发现多次，也只会保留一次。
        affected = set()
        # Star 影响整张棋盘，因此这里遍历全部位置，而不只是相邻位置。
        for other_position in grid.positions():
            dot = grid.dot_at(other_position)
            # 空格得到 None；只有真实存在且颜色相同的 Dot 才加入结果。
            if dot is not None and dot.kind == self.kind:
                affected.add(other_position)
        return affected


class SwirlDot(AbstractDot):
    """Recolour all eight surrounding dots, then remove itself."""
    asset_family = "swirl"

    # TODO 3.1：遍历周围八格，将有效可连接 Dot 改成与 SwirlDot 相同的颜色。
    def activate(self, grid, position):
        row, column = position
        # 两个循环组合出九种行列变化，也就是中心格加周围八格。
        for row_change in (-1, 0, 1):
            for column_change in (-1, 0, 1):
                # (0, 0) 没有移动，指向 Swirl 自己，因此跳过。
                if row_change == 0 and column_change == 0:
                    continue
                other_position = (row + row_change, column + column_change)
                # 先排除棋盘外坐标，否则 dot_at 会访问不存在的格子。
                if not grid.in_bounds(other_position):
                    continue
                dot = grid.dot_at(other_position)
                # 直接修改原对象的 kind，而不是创建 BasicDot；这样可以保留其 class。
                if dot is not None and dot.connectable:
                    dot.kind = self.kind
        # Swirl 改色后只移除自己，邻居仍留在棋盘上。
        return {position}


class BeamDot(AbstractDot):
    """A beam whose direction determines whether it affects a row, column, or both."""

    asset_family = "beam"
    valid_directions = ("horizontal", "vertical", "cross")

    # TODO 4.1：保存方向，并根据方向返回整行、整列或两者并集。
    def __init__(self, kind, direction):
        # 先让父类保存颜色，再处理 Beam 自己特有的方向状态。
        super().__init__(kind)
        # 尽早拒绝未知方向，避免 activate 得到一个无法解释的状态。
        if direction not in self.valid_directions:
            raise ValueError("Unknown beam direction: " + direction)
        self.direction = direction
        # View 使用同一个方向字符串选择对应的图片文件夹。
        self.asset_variant = direction

    def activate(self, grid, position):
        row, column = position
        affected = set()
        # cross 同时满足两个判断，因此会先加入整行，再加入整列。
        if self.direction in {"horizontal", "cross"}:
            for item in range(grid.columns):
                affected.add((row, item))
        if self.direction in {"vertical", "cross"}:
            for item in range(grid.rows):
                affected.add((item, column))
        # set 会自动合并 cross 中行列交叉处的重复位置。
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
        # hits_remaining 是对象自己的状态，会在两次不同的命中之间保留下来。
        self.hits_remaining = hits_remaining
        # ShellDot 会传入 1，因此同一个构造逻辑也能选择 shell 图片。
        self.asset_family = "turtle" if hits_remaining == 2 else "shell"

    def take_hit(self):
        # 每次范围效果命中时只扣除一点耐久。
        self.hits_remaining -= 1
        if self.hits_remaining == 1:
            # 第一次命中只改变状态和图片，False 告诉 Game 暂时不要删除。
            self.asset_family = "shell"
            return False
        # 第二次命中返回 True，Game 才会把当前位置加入最终移除集合。
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
        # 从下一行开始向下扫描；不需要再次检查 Anchor 当前所在位置。
        for next_row in range(row + 1, grid.rows):
            # 找到任意非 blocked 格，说明这一列下方仍有可玩的落点。
            if not grid.is_blocked((next_row, column)):
                return False
        # 扫描到底都没有找到可玩格，Anchor 已经到达该列底部。
        return True
