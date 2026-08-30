"""Stage 2 教学配置。

请确保只有一个配置块处于启用状态。要更换课程配置，请先注释当前配置块，
再取消注释或编写另一个配置块。每项注册的格式为
``(DotClass, relative_weight)``。权重必须为正数，但不需要合计为 100。
"""

from companion import (
    BuffaloCompanion, CaptainCompanion, EskimoCompanion, StarCompanion,
)
from dot import (
    AnchorDot, BasicDot, BeamDot, CompanionDot, FlowerDot, ShellDot, StarDot,
    SwirlDot, TurtleDot, WildcardDot,
)


# ============================================================================
# 当前启用的配置——Flower 入门
# 最简单的特殊 Dot：Flower 会消除自身及其正交邻居。
# 本课不使用 Companion。
# ============================================================================

ENABLED_DOT_TYPES = [
    (BasicDot, 88),
    (FlowerDot, 12),
]
COMPANION_TYPE = None


# ============================================================================
# 可直接使用的示例
# 要使用某个示例，请注释上方当前启用的配置块，并且只在下方一个配置块中
# 同时取消注释 ENABLED_DOT_TYPES 和 COMPANION_TYPE。
# ============================================================================

# --- Companion 入门：Star ----------------------------------------------------
# CompanionDot 为 StarCompanion 充能。随机补充中有意不包含 StarDot，
# 因此棋盘上的每个 Star 都能明确看出是由 Companion 生成的。
# ENABLED_DOT_TYPES = [
#     (BasicDot, 82),
#     (CompanionDot, 18),
# ]
# COMPANION_TYPE = StarCompanion


# --- Beam 方向 ---------------------------------------------------------------
# Factory 使用同一个 BeamDot 类，并从 horizontal、vertical、cross 中随机选择方向。
# ENABLED_DOT_TYPES = [
#     (BasicDot, 80),
#     (BeamDot, 20),
# ]
# COMPANION_TYPE = None


# --- 颜色规则：Swirl 与 Wildcard --------------------------------------------
# Swirl 改变附近的颜色；Wildcard 改变连接规则。
# ENABLED_DOT_TYPES = [
#     (BasicDot, 80),
#     (SwirlDot, 10),
#     (WildcardDot, 10),
# ]
# COMPANION_TYPE = None


# --- Companion 拓展：Eskimo 与 Swirl ----------------------------------------
# 随机补充中不包含 SwirlDot；它只会在被消除的 CompanionDot 为
# EskimoCompanion 充满能量后出现。
# ENABLED_DOT_TYPES = [
#     (BasicDot, 82),
#     (CompanionDot, 18),
# ]
# COMPANION_TYPE = EskimoCompanion


# --- Companion 拓展：Buffalo 与 Wildcard ------------------------------------
# 随机补充中不包含 WildcardDot；BuffaloCompanion 充满后会将若干存活 Dot
# 转换成 WildcardDot。
# ENABLED_DOT_TYPES = [
#     (BasicDot, 82),
#     (CompanionDot, 18),
# ]
# COMPANION_TYPE = BuffaloCompanion


# --- Companion 拓展：Captain 与 Beam ----------------------------------------
# 随机补充中不包含 BeamDot；CaptainCompanion 充满后会将若干存活 Dot
# 转换成随机方向、颜色不变的 BeamDot。
# ENABLED_DOT_TYPES = [
#     (BasicDot, 82),
#     (CompanionDot, 18),
# ]
# COMPANION_TYPE = CaptainCompanion


# --- Turtle 与 Shell 状态 ----------------------------------------------------
# Turtle 需要受到两次范围效果命中：第一次会变为 Shell 外观，第二次会被消除。
# Shell 从隐藏状态开始，只需命中一次。Flower 便于触发和观察这两种状态变化。
# ENABLED_DOT_TYPES = [
#     (BasicDot, 76),
#     (FlowerDot, 12),
#     (TurtleDot, 8),
#     (ShellDot, 4),
# ]
# COMPANION_TYPE = None


# --- Anchor 生命周期 ---------------------------------------------------------
# Beam 会腾出空间；Anchor 到达所在列最低的可玩位置后会被收集。
# ENABLED_DOT_TYPES = [
#     (BasicDot, 82),
#     (BeamDot, 10),
#     (AnchorDot, 8),
# ]
# COMPANION_TYPE = None


# ============================================================================
# 学生设计的配置
# 请用任意已实现的 Dot 类和正权重替换提示内容。
# 开始时只使用两到三种类型，使每种效果都容易观察。
# ============================================================================

# --- 我的 Dot 组合 -----------------------------------------------------------
# ENABLED_DOT_TYPES = [
#     (BasicDot, 80),
#     # (YourDotClass, 20),
# ]
# COMPANION_TYPE = None


# --- 我的 Dot + Companion 组合 ----------------------------------------------
# 请加入 CompanionDot，使 Companion 能够充能。如果 Companion 会生成特殊 Dot，
# 通常不要在随机补充中加入该特殊 Dot，让玩家能清楚看出它的来源。
# ENABLED_DOT_TYPES = [
#     (BasicDot, 80),
#     (CompanionDot, 20),
#     # (AnotherDotClass, weight),
# ]
# COMPANION_TYPE = None  # 请替换为 YourCompanionClass。
