# Stage 2 — Configurable Dot and Companion System

Run from the repository root:

```powershell
pip install -r stage2/requirements.txt
python stage2/a3.py
```

Stage 2 extends the complete Stage 1 game with a polymorphic, weighted dot
factory. The default board mixes `BasicDot`, `CompanionDot`, `FlowerDot`,
`SwirlDot`, horizontal/vertical/cross beam dots, and `WildcardDot`.

`ShellDot`, `TurtleDot`, and `AnchorDot` are available as challenge types and
can be added to `enabled_dot_types`. Shell and turtle need two range-effect
hits; anchors are collected after falling to the bottom of a gravity segment.

Companion dots charge an interchangeable `AbstractCompanion`. The default
`EskimoCompanion` creates swirl dots; `GardenerCompanion` demonstrates a
second implementation by creating a flower dot. Charge is displayed by the
segmented `IntervalBar`.

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

Run the model tests with:

```powershell
python -m unittest discover -s stage2/tests -v
```
