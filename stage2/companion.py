"""Chargeable helpers which demonstrate composition and polymorphism."""

from abc import ABC, abstractmethod
import random
from typing import Any, Iterable, Optional

from cell import Position
from dot import BeamDot, StarDot, SwirlDot, WildcardDot


class AbstractCompanion(ABC):
    def __init__(self, charge_limit: int = 6) -> None:
        if charge_limit <= 0:
            raise ValueError("charge_limit must be positive")
        self.charge_limit = charge_limit
        self.charge = 0

    # TODO 2.2：累加 charge；达到上限时清零并调用子类的 activate。
    def add_charge(self, amount, grid, excluded=()):
        # 返回激活次数，而不是只返回 True/False，这样一次获得大量 charge 也能处理。
        activations = 0
        # 逐点增加方便在同一个循环中检查每次是否刚好达到上限。
        for _ in range(max(0, amount)):
            self.charge += 1
            if self.charge >= self.charge_limit:
                # 先清零再激活，使 activate 期间读取到的是新一轮 charge 状态。
                self.charge = 0
                # 这里会自动调用实际对象所属子类重写的 activate 方法。
                self.activate(grid, excluded)
                activations += 1
        return activations

    def reset(self) -> None:
        self.charge = 0

    @abstractmethod
    def activate(self, grid: Any, excluded: Iterable[Position] = ()) -> None:
        pass


class StarCompanion(AbstractCompanion):
    """Turn one surviving dot into a same-colour StarDot when charged."""

    def __init__(self, charge_limit: int = 6,
                 rng: Optional[random.Random] = None) -> None:
        super().__init__(charge_limit)
        self.rng = rng if rng is not None else random.Random()

    # TODO 2.4：从未被排除的存活可连接 Dot 中随机选择一个，
    # 并通过工厂将它替换成与原 Dot 同色的 StarDot。
    def activate(self, grid, excluded=()):
        # 第一步只收集“可以被替换”的候选位置，不要在遍历时立刻修改棋盘。
        available = []
        for position in grid.positions():
            dot = grid.dot_at(position)
            # excluded 是本回合稍后会删除的位置；选中它会让新 Star 立即消失。
            if position not in excluded and dot is not None and dot.connectable:
                available.append(position)
        # 空列表不能交给 choice，因此只有存在候选时才继续。
        if available:
            position = self.rng.choice(available)
            current = grid.dot_at(position)
            # 读取 current.kind 保留原颜色；Factory 负责正确构造 StarDot。
            grid.set_dot(position, grid.factory.create_dot(
                kind=current.kind, dot_type=StarDot
            ))

class EskimoCompanion(AbstractCompanion):
    """Turn several surviving dots into SwirlDots when fully charged."""

    def __init__(self, charge_limit: int = 6, swirl_count: int = 3,
                 rng: Optional[random.Random] = None) -> None:
        super().__init__(charge_limit)
        self.swirl_count = max(0, swirl_count)
        self.rng = rng if rng is not None else random.Random()

    # TODO 3.2：从未被排除的存活可连接 Dot 中随机选择至多 swirl_count 个，
    # 并将它们替换成与原 Dot 同色的 SwirlDot。
    def activate(self, grid, excluded=()):
        # 候选筛选与 StarCompanion 相同，先完成读取，再统一进行替换。
        available = []
        for position in grid.positions():
            dot = grid.dot_at(position)
            if position not in excluded and dot is not None and dot.connectable:
                available.append(position)
        # 候选不足时缩小数量，避免 random.sample 抽取过多位置。
        number_to_change = min(self.swirl_count, len(available))
        chosen_positions = self.rng.sample(available, number_to_change)
        for position in chosen_positions:
            current = grid.dot_at(position)
            # 每个新 Swirl 分别继承它所替换对象的颜色。
            grid.set_dot(position, grid.factory.create_dot(
                kind=current.kind, dot_type=SwirlDot
            ))


class BuffaloCompanion(AbstractCompanion):
    """充能完成后，将若干存活 Dot 转换成 WildcardDot。"""

    def __init__(self, charge_limit: int = 6, wildcard_count: int = 3,
                 rng: Optional[random.Random] = None) -> None:
        super().__init__(charge_limit)
        self.wildcard_count = max(0, wildcard_count)
        self.rng = rng if rng is not None else random.Random()

    # For Extension：Buffalo 是新增 Companion 的完整参考示例。
    def activate(self, grid: Any, excluded: Iterable[Position] = ()) -> None:
        available = []
        for position in grid.positions():
            dot = grid.dot_at(position)
            if position not in excluded and dot is not None and dot.connectable:
                available.append(position)
        for position in self.rng.sample(
                available, min(self.wildcard_count, len(available))):
            grid.set_dot(position, grid.factory.create_dot(
                dot_type=WildcardDot
            ))


class CaptainCompanion(AbstractCompanion):
    """充能完成后，将若干存活 Dot 转换成随机方向的 BeamDot。"""

    beam_directions = BeamDot.valid_directions

    def __init__(self, charge_limit: int = 6, beam_count: int = 3,
                 rng: Optional[random.Random] = None) -> None:
        super().__init__(charge_limit)
        self.beam_count = max(0, beam_count)
        self.rng = rng if rng is not None else random.Random()

    # TODO 4.2：从未被排除的存活可连接 Dot 中随机选择至多 beam_count 个，
    # 在外部随机选择方向，再通过工厂替换成与原 Dot 同色的 BeamDot。
    def activate(self, grid, excluded=()):
        # 先建立候选列表，逻辑与前两个 Companion 保持一致，方便比较子类差异。
        available = []
        for position in grid.positions():
            dot = grid.dot_at(position)
            if position not in excluded and dot is not None and dot.connectable:
                available.append(position)
        number_to_change = min(self.beam_count, len(available))
        chosen_positions = self.rng.sample(available, number_to_change)
        for position in chosen_positions:
            current = grid.dot_at(position)
            # 方向由 Captain 在创建每个 Beam 前独立随机选择。
            direction = self.rng.choice(self.beam_directions)
            grid.set_dot(
                position,
                grid.factory.create_dot(
                    # 颜色来自原对象，类型和方向由 Captain 明确指定。
                    kind=current.kind,
                    dot_type=BeamDot,
                    direction=direction,
                ),
            )
