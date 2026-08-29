# Stage 2 Task Sheet — Special Dots and Companions

## 1. Stage 2 overview

Stage 1 used only ordinary coloured dots. Stage 2 introduces two kinds of extension:

- **special dots** live on the board and use different `activate` methods for range removal, recolouring or special connections;
- a **Companion** lives outside the board, receives charge from removed `CompanionDot` objects, and creates special dots when fully charged.

This stage focuses on inheritance, polymorphism and composition. The board, connections, scoring, gravity, refill, animation, image drawing and charge bar are supplied support code.

The tasks progress in this order:

```text
Starter example 1: FlowerDot
→ Starter example 2: CompanionDot + StarDot + StarCompanion
→ Intermediate: Beams, Swirl + EskimoCompanion
→ Advanced: Wildcard, durable obstacles and Anchor
```

> Image colours in this sheet are examples only. A special dot may appear in different colours in the game.

## 2. Supplied foundation

### 2.1 Common dot interface

<p align="center">
  <img src="../assets/dots/basic/blue.png" alt="Blue Basic Dot" width="72">
  &nbsp;&nbsp;
  <img src="../assets/dots/basic/coral.png" alt="Coral Basic Dot" width="72">
  &nbsp;&nbsp;
  <img src="../assets/dots/basic/gold.png" alt="Gold Basic Dot" width="72">
</p>

`AbstractDot` and `BasicDot` are supplied. A basic dot affects only itself:

```python
class AbstractDot(ABC):
    asset_family = "basic"
    asset_variant: Optional[str] = None
    connectable = True

    def __init__(self, kind: str) -> None:
        self.kind = kind

    def can_connect(self, other: "AbstractDot") -> bool:
        return self.connectable and other.connectable and self.kind == other.kind

    def activate(self, grid: Any, position: Position) -> Set[Position]:
        return {position}


class BasicDot(AbstractDot):
    pass
```

A special dot normally begins with this template:

```python
class MySpecialDot(AbstractDot):
    asset_family = "asset category"

    def activate(self, grid: Any, position: Position) -> Set[Position]:
        return {position}
```

### 2.2 Relationship between Dot and Companion

A `CompanionDot` is a dot on the board. A `Companion` is an off-board helper owned by `DotGame`. They are not parent and child classes.

```text
Player removes CompanionDot
→ DotGame counts it
→ Companion gains charge
→ full Companion activates
→ a new special dot is created on the board
```

Base charging, events and the charge bar are supplied. Students focus on what a Companion does when it becomes full.

### 2.3 Available interfaces

```python
grid.rows
grid.columns
grid.neighbours(position)
grid.positions()
grid.dot_at(position)
grid.set_dot(position, dot)
grid.factory.create_basic(kind)
grid.factory.create_swirl(kind)
grid.factory.create_star(kind)
```

## 3. Starter example one — FlowerDot

<p align="center">
  <img src="../assets/dots/flower/blue.png" alt="Blue Flower Dot" width="92">
</p>

A Flower removes itself and its immediate up, down, left and right neighbours. It does not affect diagonals.

### TODO 1.1 — Complete FlowerDot

Students receive this scaffold:

```python
class FlowerDot(AbstractDot):
    """Remove itself and its orthogonal neighbours."""

    asset_family = "flower"

    def activate(self, grid: Any, position: Position) -> Set[Position]:
        # TODO 1.1
        # Use grid.neighbours(position) to get valid neighbours.
        # Return a set containing this position and all neighbours.
        pass
```

**Check:**

- the return value is a set;
- a central Flower affects five positions;
- a corner Flower affects only three positions;
- supplied board and resolution code are unchanged.

This task demonstrates a special dot without using a Companion.

## 4. Starter example two — CompanionDot, StarDot and StarCompanion

<p align="center">
  <img src="../assets/dots/companion/purple.png" alt="Purple Companion Dot" width="92">
  &nbsp;&nbsp;&nbsp;&nbsp;
  <span>→ charge →</span>
  &nbsp;&nbsp;&nbsp;&nbsp;
  <img src="../assets/dots/star/purple.png" alt="Purple Star Dot" width="92">
</p>

This combination demonstrates how a dot and a Companion cooperate:

- `CompanionDot` lives on the board and connects like a basic dot of the same colour;
- when actually removed, it provides one charge;
- when full, `StarCompanion` changes one surviving dot into a same-colour `StarDot`;
- when the player later connects the Star, it removes every dot of that colour.

Normal refill in this combination creates only `BasicDot` and `CompanionDot`. A `StarDot` never appears randomly and can only be created by `StarCompanion`, making the source of the charged effect unambiguous.

### TODO 2.1 — Complete CompanionDot

`CompanionDot` reuses the basic dot's activation behaviour:

```python
class CompanionDot(BasicDot):
    # TODO 2.1: set the correct asset category
    asset_family = "..."
```

### TODO 2.2 — Complete StarDot

A Star keeps a colour and participates in ordinary same-colour connections:

```python
class StarDot(BasicDot):
    asset_family = "star"

    def activate(self, grid: Any, position: Position) -> Set[Position]:
        # TODO 2.2
        # Return every position containing a dot of this colour.
        pass
```

Use `grid.positions_of_kind(self.kind)`.

### TODO 2.3 — Complete StarCompanion.activate

`AbstractCompanion` already supplies charging and reset behaviour. Students complete only the Star Companion's full-charge effect:

```python
class StarCompanion(AbstractCompanion):
    def activate(self, grid: Any,
                 excluded: Iterable[Position] = ()) -> None:
        # TODO 2.3
        # 1. Find surviving, connectable dots outside excluded.
        # 2. Randomly select one position.
        # 3. Use grid.factory.create_star to create a same-colour StarDot.
        pass
```

`excluded` contains positions that will be removed in the current move, so the Companion must not select them.

**Check:**

- basic dots do not provide Companion charge;
- each removed `CompanionDot` provides one charge;
- the board does not receive a Companion effect before full charge;
- Stars are never created by normal board refill;
- full charge creates one Star matching the original dot's colour;
- connecting a Star removes every dot of that colour;
- the Companion does not modify a dot awaiting removal.

## 5. Intermediate tasks — More dots and Companion combinations

Complete class scaffolds are no longer supplied in this section. Students write the classes from the effect descriptions.

### TODO 3.1 — BeamDot family

<p align="center">
  <img src="../assets/dots/beam/horizontal/blue.png" alt="Horizontal Beam" width="82">
  &nbsp;&nbsp;&nbsp;
  <img src="../assets/dots/beam/vertical/gold.png" alt="Vertical Beam" width="82">
  &nbsp;&nbsp;&nbsp;
  <img src="../assets/dots/beam/cross/purple.png" alt="Cross Beam" width="82">
</p>

First create the common `BeamDot` parent:

- use `asset_family = "beam"`;
- store a `direction`;
- expose that direction through a read-only `asset_variant` property.

Then create three subclasses:

- `HorizontalBeamDot` returns its entire row;
- `VerticalBeamDot` returns its entire column;
- `CrossBeamDot` combines its entire row and column.

**Check:** on an 8×8 board, the horizontal and vertical Beams affect eight positions each, while the Cross Beam affects 15 different positions.

### TODO 3.2 — SwirlDot

<p align="center">
  <img src="../assets/dots/swirl/coral.png" alt="Coral Swirl Dot" width="92">
</p>

When a `SwirlDot` activates:

1. inspect all eight surrounding cells, including diagonals;
2. skip itself, empty cells and non-connectable obstacles;
3. replace valid neighbours with `BasicDot` objects matching the Swirl's colour;
4. return only the Swirl's own position.

**Check:** only valid surrounding dots are changed, and only the Swirl itself is removed.

### TODO 3.3 — EskimoCompanion

<p align="center">
  <img src="../assets/dots/companion/blue.png" alt="Blue Companion Dot" width="82">
  &nbsp;&nbsp;&nbsp;&nbsp;
  <span>→ charge →</span>
  &nbsp;&nbsp;&nbsp;&nbsp;
  <img src="../assets/dots/swirl/blue.png" alt="Blue Swirl Dot" width="92">
</p>

Implement `EskimoCompanion.activate`:

- find surviving, connectable dots outside `excluded`;
- randomly select at most `swirl_count` positions;
- replace each with a `SwirlDot` matching the original dot's colour;
- if too few candidates exist, convert only the available candidates without raising an error.

This combination demonstrates that the same `CompanionDot` can charge interchangeable Companions, while each Companion creates a different special dot.

## 6. Advanced extensions

### Extension 4.1 — WildcardDot

<p align="center">
  <img src="../assets/dots/wildcard.png" alt="Wildcard Dot" width="92">
</p>

A Wildcard has no fixed colour and may connect to any connectable dot. Create `WildcardDot`, use `"wildcard"` as its default `kind`, and override `can_connect(other)`.

Connection-colour selection, backtracking and loop rules are supplied.

### Extension 4.2 — ShellDot and TurtleDot

<p align="center">
  <img src="../assets/dots/shell.png" alt="Shell Dot" width="92">
  &nbsp;&nbsp;&nbsp;&nbsp;
  <img src="../assets/dots/turtle.png" alt="Turtle Dot" width="92">
</p>

A Turtle is a non-connectable, two-stage durable obstacle. The first range-effect hit makes it hide and change from the Turtle image to the Shell image. The second hit removes it. `ShellDot` represents a Turtle which starts hidden, so it needs only one more hit.

First create a shared `DurableDot` parent:

- set `connectable = False`;
- use a maximum durability of two;
- store remaining durability in the constructor;
- make `take_hit()` reduce durability and return whether removal is now required.

Then implement `TurtleDot` so its remaining durability dynamically selects the `"turtle"` or `"shell"` asset family. Finally, derive `ShellDot` from `TurtleDot`, but start it with one remaining hit.

**Check:** after the first hit, a Turtle remains the same object but displays the Shell image; the second hit removes it; a directly created Shell is removed by one hit. Random Turtle movement is not part of this stage.

### Extension 4.3 — AnchorDot

<p align="center">
  <img src="../assets/dots/anchor.png" alt="Anchor Dot" width="92">
</p>

An Anchor cannot be connected. It falls under gravity and is collected at the lowest playable position in its column. Students implement only the Anchor asset category and non-connectable property; gravity and collection are supplied.

## 7. Recommended test combinations

Enable only two or three dot types at a time so each effect is easy to observe.

| Learning focus | Dot combination | Companion |
| --- | --- | --- |
| Flower starter | Basic + Flower | None |
| Companion starter | Basic + CompanionDot | Star |
| Beams | Basic + Horizontal + Vertical | None |
| Swirl and Companion | Basic + CompanionDot | Eskimo |
| Turtle state change | Basic + Flower + Turtle | None |
| Anchor | Basic + Horizontal + Anchor | None |

## 8. Completion checklist

- explain why `CompanionDot` and `Companion` are different objects;
- `FlowerDot` correctly affects orthogonal neighbours;
- a Companion receives charge only from removed `CompanionDot` objects;
- StarCompanion creates Stars and Eskimo creates Swirls;
- all three Beam directions have the correct effect;
- `SwirlDot` correctly changes surrounding dots;
- a Turtle changes to its Shell appearance after one hit and disappears after the next;
- animation, gravity, scoring and the charge bar are not copied into student classes;
- teacher-selected extensions pass their tests.

## 9. Run and validate

Keep only one configuration block active in `config.py`. Students may edit Dot
types and relative weights directly, for example:

```python
ENABLED_DOT_TYPES = [
    (BasicDot, 76),
    (FlowerDot, 12),
    (TurtleDot, 8),
    (ShellDot, 4),
]
COMPANION_TYPE = None
```

```powershell
python -m unittest discover -s stage2/tests -v
python stage2/a3.py
```

After the automated tests pass, visually inspect images, connections, Companion charge and special effects in the GUI.
