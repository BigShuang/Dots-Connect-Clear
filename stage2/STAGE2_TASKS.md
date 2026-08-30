# Stage 2 Task Sheet — Building Dots and Companions with Classes

## 1. Learning path

Stage 2 keeps GUI, animation, gravity, scoring, and Factory code supplied.
Students implement meaningful algorithms inside small classes and methods.

Companion foundations come before every concrete Companion and its associated
Dot. Each concrete pair is then completed as one runnable feature group:

```text
TODO 1.1  FlowerDot

TODO 2.1  count removed CompanionDots
TODO 2.2  AbstractCompanion.add_charge
TODO 2.3  StarDot
TODO 2.4  StarCompanion
            ↓ run the first complete charge ability

TODO 3.1  SwirlDot
TODO 3.2  EskimoCompanion
            ↓ run the second ability

TODO 4.1  BeamDot
TODO 4.2  CaptainCompanion
            ↓ run the third ability

TODO 5.1  TurtleDot state
Extension 5.2  Anchor lifecycle
```

Later tasks may depend on earlier tasks; earlier tasks never depend on later
ones. Intermediate tasks use focused tests. Enable a feature group's GUI config
only after both its Dot and Companion are complete.

- `TODO X`: students implement task X.
- `For X`: complete code supplied to support task X.

## 2. Supplied foundations

All Dots inherit `AbstractDot` and provide `kind`, `connectable`,
`asset_family`, and `activate(grid, position)`.

Students may use `grid.rows`, `grid.columns`, `grid.in_bounds`,
`grid.positions`, `grid.dot_at`, `grid.set_dot`, and `grid.is_blocked`.

Factory is `For` code. Students call its single creation entry point:

```python
grid.factory.create_dot(kind="blue", dot_type=StarDot)
grid.factory.create_dot(kind="blue", dot_type=SwirlDot)
grid.factory.create_dot(kind="blue", dot_type=BeamDot, direction="cross")
```

## 3. Phase one — Special-Dot introduction

### TODO 1.1 — FlowerDot

In `FlowerDot.activate`, calculate up, down, left, and right with a loop. Use
`grid.in_bounds` and return a set containing the Flower and valid neighbours.
Do not call `grid.neighbours`; coordinate and boundary logic are the task.

The active starter config displays this result immediately.

## 4. Phase two — Companion foundations and the Star pair

This first group builds the complete shared workflow:

```text
remove CompanionDot → count it → gain charge → reset and activate
→ StarCompanion creates StarDot → StarDot clears its colour
```

### TODO 2.1 — Count removed CompanionDots

Implement `DotGame.count_companion_dots(positions)`. Traverse only final
removal positions, use `isinstance(dot, CompanionDot)`, count matches, and
return the count. Indirect removals must count; objects outside the final set
must not. Verify it with its focused test.

### TODO 2.2 — AbstractCompanion.add_charge

Add charge one point at a time. Whenever the limit is reached, reset to zero,
call `activate(grid, excluded)`, and count the activation. Return the total
activations. Tests use a small test double, so this task does not depend on a
later concrete Companion.

### TODO 2.3 — StarDot

Traverse `grid.positions()`, read each Dot, compare its `kind` with
`self.kind`, and collect all matching positions. Do not use
`positions_of_kind`; iteration and filtering are the core algorithm.

### TODO 2.4 — StarCompanion.activate

Collect surviving connectable Dots outside `excluded`, handle no candidates,
choose one randomly, preserve its colour, and replace it with a Factory-created
`StarDot`.

Now enable the `TODO 2.1–2.4` config. StarDot is created only by
StarCompanion, making the complete feature chain visible.

## 5. Phase three — The Swirl and Eskimo pair

### TODO 3.1 — SwirlDot

Use two small loops to visit the eight surrounding cells. Skip the centre,
out-of-bounds positions, empty cells, and non-connectable objects. Change each
eligible Dot's `kind` and return only the Swirl position. Recolouring must
preserve the neighbour's class.

### TODO 3.2 — EskimoCompanion.activate

Select up to `swirl_count` eligible positions, preserve their colours, and
replace them with Factory-created `SwirlDot` objects. Use all available
candidates when fewer than requested exist.

Enable the `TODO 3.1–3.2` config. Swirls are created only by EskimoCompanion.

## 6. Phase four — The Beam and Captain pair

### TODO 4.1 — BeamDot

Complete one simple class that stores `kind` and `direction`. Valid directions
are `horizontal`, `vertical`, and `cross`; reject other values and set
`asset_variant` to the direction. Use ordinary loops to return a row, column,
or their union. Factory's `For 4.1` branch chooses a random direction when one
is not supplied.

### TODO 4.2 — CaptainCompanion.activate

Select up to `beam_count` eligible positions. For each, preserve its colour,
choose a valid direction, and create a `BeamDot` through Factory.

Enable the `TODO 4.1–4.2` config. Beams are created only by CaptainCompanion.

## 7. Phase five — State and lifecycle extensions

### TODO 5.1 — TurtleDot.take_hit

A Turtle starts non-connectable with two hits and the `turtle` image. The first
range hit changes it to `shell` and returns `False`; the second returns `True`
so Game removes it. Implement this in one class. `ShellDot` is a `For 5.1`
reuse example. The matching config uses the already completed FlowerDot.

### Extension 5.2 — AnchorDot.has_landed

Scan below the Anchor in its column. Return `False` if any playable position
remains below; otherwise return `True`. Game asks the Anchor after gravity and
collects it when it has landed.

## 8. For Extension example

`WildcardDot` and `BuffaloCompanion` remain a complete fourth Dot–Companion
pair for comparison and independent extension. They are not student TODOs.

## 9. Run and validate

Run focused tests after intermediate tasks. After completing a feature group,
enable only its matching config and launch the GUI:

```powershell
python -m unittest discover -s stage2/tests -v
python stage2/a3.py
```

Every feature group must run without a later unfinished TODO. Students should
be able to explain whether each class creates objects, changes state, or
calculates removal positions.
