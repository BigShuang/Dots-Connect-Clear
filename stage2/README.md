# Stage 2 — Configurable Dot and Companion System

Run from the repository root:

```powershell
pip install -r stage2/requirements.txt
python stage2/a3.py
```

Stage 2 extends the complete Stage 1 game with a polymorphic, weighted dot
factory. The system supports `BasicDot`, `CompanionDot`, `FlowerDot`,
`StarDot`, `SwirlDot`, one direction-configured `BeamDot`, and `WildcardDot`;
the GUI uses the small Starter Flower configuration by default to avoid visual
and conceptual overload.

`TurtleDot`, `ShellDot`, and `AnchorDot` are available as challenge types. A
turtle changes to its shell appearance after one range-effect hit and is
removed by the next hit. `ShellDot` starts in that second state and therefore
needs one hit. Anchors are collected after falling to the bottom of a gravity
segment.

Companion dots charge an interchangeable `AbstractCompanion`.
`StarCompanion` creates one same-colour star, `EskimoCompanion` creates swirl
dots, `BuffaloCompanion` creates wildcards, and `CaptainCompanion` creates
randomly oriented same-colour beams. Companion-created special dots can be
left out of random refill so their source is clear. Charge is displayed by the
segmented `IntervalBar`.

Stage 2 reuses the complete Stage 1 support-code animation contract: removed
dots shrink, surviving dots fall smoothly, and replacements enter from above.
The centre block does not split gravity into separate upper/lower generators;
dots fall through its columns and are visually hidden while passing behind the
foreground block. Special-dot and companion rules remain model concerns and
use the same `begin/remove/fall/fill` phases.

Stage 2 is built on the current Stage 1S foundation: the application startup,
menu and shortcut handling, status panel, reset flow, confirmation dialog, and
game-result dialogs keep the Stage 1S behaviour. Stage 2 adds its configurable
dot system and companion UI on top of that shared flow.

## Configuration

Stage 2 uses `config.py` for its teaching configuration. The comments in
this file explain in Chinese how to select Dot types, relative weights, and a
Companion for a lesson.

Pass registrations to `DotFactory` to change the board without editing the
grid or game loop:

```python
factory = DotFactory(enabled_dot_types=[
    (BasicDot, 80),
    (FlowerDot, 10),
    (BeamDot, 10),
])
game = DotGame(factory=factory)
```

`DotFactory.create_dot` is the single creation entry point. With no explicit
type it uses the configured weights; callers may pass `dot_type`, `kind`, and
an optional Beam `direction` when creating a specific Dot. `TODO X` marks code
students implement; `For X` marks complete code that supports the same task.

Weights only need to be positive; they do not need to add to 100. Stage 2
deliberately resolves one activation layer. Range effects remove or damage
their targets but do not recursively activate other special dots. Recursive
chains, moving balloons/butterflies, and target-selecting companions belong to
Stage 3.

## Recommended combinations

Normal teaching runs should use only two or three Dot types. Open
`config.py`, keep exactly one configuration block active, and edit the Dot
classes and relative weights directly:

```python
ENABLED_DOT_TYPES = [
    (BasicDot, 88),
    (FlowerDot, 12),
]
COMPANION_TYPE = None
```

| Commented example | Dot types | Companion | Recommended use |
| --- | --- | --- | --- |
| Starter Flower (active) | Basic, Flower | None | First activation override; easiest |
| Companion introduction | Basic, CompanionDot | Star | Star is Companion-only |
| Beam directions | Basic, BeamDot | None | One class with externally selected direction |
| Colour rules | Basic, Swirl, Wildcard | None | Board mutation and connection rules |
| Companion extension | Basic, CompanionDot | Eskimo | Companion creates Swirl dots |
| Wildcard companion | Basic, CompanionDot | Buffalo | Companion creates Wildcards |
| Beam companion | Basic, CompanionDot | Captain | Companion creates random Beams |
| Turtle and Shell states | Basic, Flower, Turtle, Shell | None | Compare both starting states |
| Anchor lifecycle | Basic, BeamDot, Anchor | None | Post-gravity lifecycle hook |

All examples are complete commented code blocks ready to uncomment. Two final
templates are deliberately left for student-designed Dot and Dot+Companion
combinations. `game.py` imports the active values and remains focused on game
rules.

Run the model tests with:

```powershell
python -m unittest discover -s stage2/tests -v
```
