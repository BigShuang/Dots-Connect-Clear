# Stage 2 — Configurable Dot and Companion System

Run from the repository root:

```powershell
pip install -r stage2/requirements.txt
python stage2/a3.py
```

Stage 2 extends the complete Stage 1 game with a polymorphic, weighted dot
factory. The system supports `BasicDot`, `CompanionDot`, `FlowerDot`,
`SwirlDot`, horizontal/vertical/cross beam dots, and `WildcardDot`; the GUI
uses the small `starter_flower` combination by default to avoid visual and
conceptual overload.

`ShellDot`, `TurtleDot`, and `AnchorDot` are available as challenge types and
can be added to `enabled_dot_types`. Shell and turtle need two range-effect
hits; anchors are collected after falling to the bottom of a gravity segment.

Companion dots charge an interchangeable `AbstractCompanion`. The default
`EskimoCompanion` creates swirl dots; `GardenerCompanion` demonstrates a
second implementation by creating a flower dot. Charge is displayed by the
segmented `IntervalBar`.

Stage 2 reuses the complete Stage 1 support-code animation contract: removed
dots shrink, surviving dots fall smoothly, and replacements enter from above.
The centre block does not split gravity into separate upper/lower generators;
dots fall through its columns and are visually hidden while passing behind the
foreground block. Special-dot and companion rules remain model concerns and
use the same `begin/remove/fall/fill` phases.

## Configuration

Pass registrations to `DotFactory` to change the board without editing the
grid or game loop:

```python
factory = DotFactory(enabled_dot_types=[
    (BasicDot, 80),
    (FlowerDot, 10),
    (HorizontalBeamDot, 10),
])
game = DotGame(factory=factory)
```

Weights only need to be positive; they do not need to add to 100. Stage 2
deliberately resolves one activation layer. Range effects remove or damage
their targets but do not recursively activate other special dots. Recursive
chains, moving balloons/butterflies, and target-selecting companions belong to
Stage 3.

## Recommended combinations

Normal teaching runs should use only two or three Dot types. Open `game.py`
and directly edit these two values:

```python
ENABLED_DOT_TYPES = [
    (BasicDot, 88),
    (FlowerDot, 12),
]
COMPANION_TYPE = None
```

| Dot types | Companion | Recommended use |
| --- | --- | --- |
| Basic, Flower | None | First activation override; easiest |
| Basic, horizontal Beam, vertical Beam | None | Compare sibling subclasses |
| Basic, Swirl, Wildcard | None | Board mutation and connection rules |
| Basic, CompanionDot | Eskimo | First charge/composition exercise |
| Basic, CompanionDot, Flower | Gardener | Compare interchangeable companions |
| Basic, Flower, Shell | None | Mutable two-hit state |
| Basic, horizontal Beam, Anchor | None | Post-gravity lifecycle hook |

The same lists appear as comments beside the settings, ready to copy.

Run the model tests with:

```powershell
python -m unittest discover -s stage2/tests -v
```
