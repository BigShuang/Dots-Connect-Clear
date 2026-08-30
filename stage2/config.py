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

# --- TODO 2.1–2.4：Companion 基础与 Star 第一组能力 --------------------------
# 依次完成 CompanionDot 统计、charge、StarDot 和 StarCompanion。
# Star 只由充满的 StarCompanion 生成；整组完成后再启用本配置。
# ENABLED_DOT_TYPES = [
#     (BasicDot, 82),
#     (CompanionDot, 18),
# ]
# COMPANION_TYPE = StarCompanion


# --- TODO 3.1–3.2：SwirlDot 与 EskimoCompanion -------------------------------
# Swirl 只由充满的 EskimoCompanion 生成；完成整组后启用。
# ENABLED_DOT_TYPES = [
#     (BasicDot, 82),
#     (CompanionDot, 18),
# ]
# COMPANION_TYPE = EskimoCompanion


# --- TODO 4.1–4.2：BeamDot 与 CaptainCompanion -------------------------------
# Beam 只由充满的 CaptainCompanion 生成；方向由 Factory 随机选择。
# ENABLED_DOT_TYPES = [
#     (BasicDot, 82),
#     (CompanionDot, 18),
# ]
# COMPANION_TYPE = CaptainCompanion


# --- TODO 5.1：Turtle 状态 ---------------------------------------------------
# Flower 方便连续命中 Turtle：第一次变成 Shell，第二次消失。
# ENABLED_DOT_TYPES = [
#     (BasicDot, 80),
#     (FlowerDot, 12),
#     (TurtleDot, 8),
# ]
# COMPANION_TYPE = None


# --- Extension 5.2：Anchor 生命周期 -----------------------------------------
# Beam 会腾出空间；Anchor 到达所在列最低的可玩位置后会被收集。
# ENABLED_DOT_TYPES = [
#     (BasicDot, 82),
#     (BeamDot, 10),
#     (AnchorDot, 8),
# ]
# COMPANION_TYPE = None


# --- For Extension：Wildcard 与 Buffalo ------------------------------------
# 这是新增 Dot/Companion 组合的完整参考示例，不属于学生 TODO。
# ENABLED_DOT_TYPES = [
#     (BasicDot, 82),
#     (CompanionDot, 18),
# ]
# COMPANION_TYPE = BuffaloCompanion


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
