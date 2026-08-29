"""Stage 2 teaching configuration.

Keep exactly one configuration block active.  Comment out the current block,
then uncomment or write another block to change the lesson.  Each registration
is ``(DotClass, relative_weight)``.  Weights must be positive, but they do not
need to add to 100.
"""

from companion import EskimoCompanion, StarCompanion
from dot import (
    AnchorDot, BasicDot, CompanionDot, CrossBeamDot, FlowerDot,
    HorizontalBeamDot, ShellDot, StarDot, SwirlDot, TurtleDot,
    VerticalBeamDot, WildcardDot,
)


# ============================================================================
# ACTIVE CONFIGURATION — Starter Flower
# The easiest special Dot: Flower removes itself and orthogonal neighbours.
# No Companion is used in this lesson.
# ============================================================================

ENABLED_DOT_TYPES = [
    (BasicDot, 88),
    (FlowerDot, 12),
]
COMPANION_TYPE = None


# ============================================================================
# READY-TO-USE EXAMPLES
# To use one example, comment out the active block above and uncomment both
# ENABLED_DOT_TYPES and COMPANION_TYPE in exactly one block below.
# ============================================================================

# --- Companion introduction: Star -------------------------------------------
# CompanionDot charges StarCompanion.  StarDot is intentionally absent from
# random refill, so every Star on the board clearly comes from the Companion.
# ENABLED_DOT_TYPES = [
#     (BasicDot, 82),
#     (CompanionDot, 18),
# ]
# COMPANION_TYPE = StarCompanion


# --- Beam family -------------------------------------------------------------
# Compare sibling subclasses.  CrossBeamDot is rarer because it affects both
# its row and column.
# ENABLED_DOT_TYPES = [
#     (BasicDot, 80),
#     (HorizontalBeamDot, 8),
#     (VerticalBeamDot, 8),
#     (CrossBeamDot, 4),
# ]
# COMPANION_TYPE = None


# --- Colour rules: Swirl and Wildcard ---------------------------------------
# Swirl changes nearby colours; Wildcard changes connection rules.
# ENABLED_DOT_TYPES = [
#     (BasicDot, 80),
#     (SwirlDot, 10),
#     (WildcardDot, 10),
# ]
# COMPANION_TYPE = None


# --- Companion extension: Eskimo and Swirl ----------------------------------
# SwirlDot is absent from random refill.  It appears only when EskimoCompanion
# has been charged by removed CompanionDots.
# ENABLED_DOT_TYPES = [
#     (BasicDot, 82),
#     (CompanionDot, 18),
# ]
# COMPANION_TYPE = EskimoCompanion


# --- Turtle and Shell states -------------------------------------------------
# Turtle needs two range hits: the first changes it to the Shell appearance;
# the second removes it.  Shell starts hidden and needs one hit.  Flower makes
# both state changes easy to trigger and observe.
# ENABLED_DOT_TYPES = [
#     (BasicDot, 76),
#     (FlowerDot, 12),
#     (TurtleDot, 8),
#     (ShellDot, 4),
# ]
# COMPANION_TYPE = None


# --- Anchor lifecycle --------------------------------------------------------
# Horizontal Beam creates space; Anchor is collected after reaching the lowest
# playable position in its column.
# ENABLED_DOT_TYPES = [
#     (BasicDot, 82),
#     (HorizontalBeamDot, 10),
#     (AnchorDot, 8),
# ]
# COMPANION_TYPE = None


# ============================================================================
# STUDENT-DESIGNED CONFIGURATIONS
# Replace the hints with any implemented Dot classes and positive weights.
# Start with only two or three types so each effect remains easy to observe.
# ============================================================================

# --- My Dot combination ------------------------------------------------------
# ENABLED_DOT_TYPES = [
#     (BasicDot, 80),
#     # (YourDotClass, 20),
# ]
# COMPANION_TYPE = None


# --- My Dot + Companion combination -----------------------------------------
# Include CompanionDot so the Companion can charge.  If the Companion creates
# a special Dot, normally leave that special Dot out of random refill so its
# source is clear to the player.
# ENABLED_DOT_TYPES = [
#     (BasicDot, 80),
#     (CompanionDot, 20),
#     # (AnotherDotClass, weight),
# ]
# COMPANION_TYPE = None  # Replace with YourCompanionClass.
