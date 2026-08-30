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

### 2.1 Visual guide

<table>
  <tr><td align="center" width="90"><img src="../assets/dots/basic/blue.png" width="54" alt="BasicDot"></td><td><strong><code>BasicDot</code></strong><br>A regular connectable coloured Dot.</td></tr>
  <tr><td align="center"><img src="../assets/dots/flower/blue.png" width="54" alt="FlowerDot"></td><td><strong><code>FlowerDot</code></strong><br>Affects itself and four orthogonal neighbours.</td></tr>
  <tr><td align="center"><img src="../assets/dots/companion/blue.png" width="54" alt="CompanionDot"></td><td><strong><code>CompanionDot</code></strong><br>Adds charge when it is actually removed.</td></tr>
  <tr><td align="center"><img src="../assets/dots/star/blue.png" width="54" alt="StarDot"></td><td><strong><code>StarDot</code></strong><br>Finds every Dot of its colour.</td></tr>
  <tr><td align="center"><img src="../assets/dots/swirl/blue.png" width="54" alt="SwirlDot"></td><td><strong><code>SwirlDot</code></strong><br>Recolours eight neighbours without changing their classes.</td></tr>
  <tr><td align="center"><img src="../assets/dots/beam/horizontal/blue.png" width="40" alt="horizontal"><img src="../assets/dots/beam/vertical/blue.png" width="40" alt="vertical"><img src="../assets/dots/beam/cross/blue.png" width="40" alt="cross"></td><td><strong><code>BeamDot</code></strong><br>Uses direction state to affect a row, column, or cross.</td></tr>
  <tr><td align="center"><img src="../assets/dots/turtle.png" width="50" alt="TurtleDot"><img src="../assets/dots/shell.png" width="50" alt="ShellDot"></td><td><strong><code>TurtleDot</code></strong><br>Changes state after the first hit and disappears after the second.</td></tr>
  <tr><td align="center"><img src="../assets/dots/anchor.png" width="54" alt="AnchorDot"></td><td><strong><code>AnchorDot</code></strong><br>Is collected after reaching the bottom of its playable column.</td></tr>
  <tr><td align="center"><img src="../assets/dots/wildcard.png" width="54" alt="WildcardDot"></td><td><strong><code>WildcardDot</code></strong><br>A supplied extension example that connects to any colour.</td></tr>
</table>

### 2.2 The common Dot interface

All Dots inherit `AbstractDot`. A class is the design for a type of Dot; each
object on the board is one instance of that design.

| Member | Meaning | Example |
| --- | --- | --- |
| `kind` | current colour | `dot.kind == "blue"` |
| `connectable` | whether the player may connect it | Turtle uses `False` |
| `asset_family` | image family | Flower uses `"flower"` |
| `asset_variant` | variation inside a family | Beam uses its direction |
| `activate(grid, position)` | behaviour when activated | returns affected positions |

Game can call the same line for every class:

```python
affected_positions = dot.activate(grid, position)
```

The actual object decides which implementation runs. This is the key
polymorphism idea in Stage 2.

### 2.3 Positions and grid methods

A position is `(row, column)`, starting from zero:

```text
          column 0   column 1   column 2
row 0       (0, 0)     (0, 1)     (0, 2)
row 1       (1, 0)     (1, 1)     (1, 2)
```

| Grid member | Purpose |
| --- | --- |
| `rows`, `columns` | board dimensions |
| `in_bounds(position)` | checks whether a coordinate exists |
| `positions()` | visits every coordinate |
| `dot_at(position)` | gets the Dot or `None` at one coordinate |
| `set_dot(position, dot)` | places or replaces an object |
| `is_blocked(position)` | checks for a blocked centre cell |

The common “traverse then filter” shape is:

```python
matching = []
for position in grid.positions():
    dot = grid.dot_at(position)
    if dot is not None and dot.connectable:
        matching.append(position)
```

### 2.4 Factory and Companion foundations

Factory is `For` code. Students call its single creation entry point:

```python
grid.factory.create_dot(kind="blue", dot_type=StarDot)
grid.factory.create_dot(kind="blue", dot_type=SwirlDot)
grid.factory.create_dot(kind="blue", dot_type=BeamDot, direction="cross")
```

`kind` chooses colour, `dot_type` chooses the class, and Beam alone may also
receive `direction`. Use `grid.set_dot` afterwards to place the new object.

`CompanionDot` is a Dot on the board; `AbstractCompanion` is a separate ability
object that keeps charge between moves. If its limit is three, the first two
removed CompanionDots leave charge at one and two. The third resets charge and
calls the concrete Companion's `activate` method.

## 3. Phase one — Special-Dot introduction

### TODO 1.1 — FlowerDot

<table>
  <tr><td align="center" width="90"><img src="../assets/dots/flower/blue.png" width="66" alt="FlowerDot"></td><td><strong><code>FlowerDot</code></strong><br>Use one small loop to practise coordinates, boundary checks, and sets.</td></tr>
</table>

In `FlowerDot.activate`, calculate up, down, left, and right with a loop. Use
`grid.in_bounds` and return a set containing the Flower and valid neighbours.
Do not call `grid.neighbours`; coordinate and boundary logic are the task.

The active starter config displays this result immediately.

For a Flower at `(1, 1)`, calculate `(0, 1)`, `(2, 1)`, `(1, 0)`, and
`(1, 2)`. Start the result set with the Flower's own position, test every
candidate with `in_bounds`, then return the completed set. A corner Flower has
only two valid neighbours, which is why the boundary check matters.

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
