# Stage 1 Task Sheet — Basic GUI and Game Flow

## 1. Purpose

Stage 1 focuses on using supplied support code to complete a working Tkinter
application. The aim is to understand the path from mouse input, through the
controller and game model, back to an updated view. Students are not expected
to rewrite the board algorithms.

The teacher version in this folder remains complete and runnable. Only comments
beginning with `# TODO 1.x`, `# TODO 2.x`, or `# TODO 3.x` are student tasks.
All other comments and docstrings are explanatory notes about supplied code;
they do not ask students to implement anything. In the current teacher version,
**do not delete or alter the implementation below a TODO comment**.

## 2. Supplied support code

The following features are already implemented and are not Stage 1 ToDos:

- connection validation and loop detection;
- dot activation, removal, gravity, refill and playable-board checks;
- scoring, objectives, moves, win and loss rules;
- non-blocking removal, fall and refill animations;
- Canvas drawing, image loading and pixel-to-grid coordinate conversion;
- the `DotGrid`, `DotGame`, `DotFactory` and dot extension interfaces.

Students should call these interfaces and trace their behaviour, not copy or
rewrite their internal algorithms.

## 3. Stage steps by feature

The tasks follow sections 4.1–4.3 of the reference assignment specification,
adapted to this project's architecture. `IntervalBar` remains outside Stage 1
and will be introduced with Companion charge in Stage 2.

### 3.1 App Class

#### TODO 1.1 — Instantiate DotsApp

In `a3.py`, instantiate `DotsApp` using the supplied root window and pack it so
that it expands to fill the entire window.

#### TODO 1.2 — Lay out GridView

Use `pack` so `GridView` fills the remaining space, resizes with the window and
has suitable horizontal and bottom margins.

**Check:** both widgets appear, resizing the window enlarges the board area,
and the program still starts through `a3.py`.

The event bindings, connection controller callbacks and animation pipeline do
not have TODO markers in the current code. Their comments are explanatory and
the implementations are supplied.

### 3.2 InfoPanel Class

#### TODO 2.1 — Create the remaining-moves area

Create and lay out the title and numeric labels that display remaining moves.
Use the requested colours and a suitable `Segoe UI Semibold` font size.

#### TODO 2.2 — Create the score area

Create and lay out the score title and numeric label using the requested text
style and horizontal `pack()` layout.

#### TODO 2.3 — Implement InfoPanel setters

Update the supplied score and remaining-moves labels. The adjacent ordinary
code shows that objectives are delegated to `ObjectivesView`.

#### TODO 2.4 — Add InfoPanel to DotsApp

Create `InfoPanel` in `DotsApp.__init__` and pack it at the top of the app.

#### TODO 2.6 — Refresh displayed game state

In `DotsApp.refresh_status`, read public `DotGame` attributes and pass score,
moves remaining and objectives to the corresponding `InfoPanel` setters.

The comments numbered 2.5 and 2.7 in `app.py` do not contain `TODO`; they only
explain the supplied event binding and initial refresh statements.

### 3.3 File Menu / Popup Dialogs

#### TODO 3.1 — Initialise menu and window commands

From `DotsApp.__init__`, create the menu and register the window-close protocol
and New Game shortcut. All of these initialisation statements belong here.

#### TODO 3.2 — Build the File menu

In `DotsApp._create_menu`, create a File menu containing New Game and Exit.
Wire those menu items to the supplied controller callbacks and attach the menu
bar to the root window.

**Check:** New Game resets the current game, Exit opens the confirmation
dialog, and `Ctrl+N` continues to start a new game.

#### TODO 3.4 — Confirm application exit

In `DotsApp.confirm_exit`, use a Tkinter message box to ask for confirmation.
Destroy the root window only when the user confirms.

#### TODO 3.5 — Show the game outcome

After resolution finishes, show an informational dialog for either a win or a
loss by reading the model's public outcome properties.

The comment numbered 3.3 beside `new_game` does not contain `TODO`; it explains
the supplied reset implementation and is not a student task.

**Menu/dialog check:** New Game resets the game; Exit and the window close
control both request confirmation; No keeps the application open; Yes closes
it; and the appropriate outcome dialog appears when the game ends.

## 4. End-to-end flow to explain

A completed submission should be able to explain this sequence:

```text
GridView mouse event
→ DotsApp callback
→ DotGame selection/resolution
→ model event
→ DotsApp/GridView refresh
→ updated board and InfoPanel
```

The animation controller divides resolution into removal, falling and refill
phases. It is supplied code: students need to identify where it is called, but
do not need to implement it.

## 5. Completion checklist

- The application launches and a complete game can be played.
- Invalid or one-dot selections do not consume a move.
- A valid move updates the board, score, moves and objectives.
- New Game resets model and view state.
- Exit confirmation handles both Yes and No correctly.
- A win or loss displays the corresponding outcome dialog.
- No Stage 2 features (`IntervalBar`, special dots, Companion or ActionBar) are
  added to Stage 1.
- No supplied model, board or animation implementation is deleted or changed.

## 6. Suggested validation

Run the automated tests from the repository root:

```powershell
python -m pytest stage1/tests
```

Then run the GUI and complete the manual checks above:

```powershell
python stage1/a3.py
```
