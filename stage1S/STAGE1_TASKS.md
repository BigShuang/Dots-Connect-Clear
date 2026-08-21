# Stage 1 Task Sheet — Basic GUI and Game Flow

## 1. Purpose

Stage 1 focuses on using supplied support code to complete a working Tkinter
application. The aim is to understand the path from mouse input, through the
controller and game model, back to an updated view. Students are not expected
to rewrite the board algorithms.

The teacher version in this folder remains complete and runnable. Comments
marked `TODO-STAGE1-*` describe the statements that may later be removed or
replaced with stubs when a separate student starter is prepared. For the
current version, **do not delete or alter the implementation below a ToDo**.

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

## 3. Required tasks

### TODO-STAGE1-1 — Compose the application GUI

In `DotsApp.__init__`, create the supplied `InfoPanel` and `GridView` with the
correct parent and lay them out vertically. The information panel must stay at
the top, while the board expands with the window.

**Check:** both widgets appear, resizing the window enlarges the board area,
and the program still starts through `a3.py`.

### TODO-STAGE1-2 — Connect events and callbacks

In `DotsApp._bind_events`, connect the view's press, drag and release callbacks
to the matching controller methods. Subscribe the view/status/reset handlers
to the supplied model events.

**Check:** dragging adjacent same-colour dots changes the selection display,
releasing completes a valid move, and resetting redraws the application.

### TODO-STAGE1-3 — Refresh model state in the view

In `DotsApp.refresh_status`, read only the public `DotGame` attributes and pass
their values to the corresponding `InfoPanel` setters.

**Check:** score, moves remaining and objectives update after every valid move
and return to their initial values after New Game.

### TODO-STAGE1-4 — Build the File menu

In `DotsApp._create_menu`, create a File menu containing New Game and Exit.
Wire those menu items to the supplied controller callbacks and attach the menu
bar to the root window.

**Check:** New Game resets the current game, Exit opens the confirmation
dialog, and `Ctrl+N` continues to start a new game.

### TODO-STAGE1-5 — Confirm application exit

In `DotsApp.confirm_exit`, use a Tkinter message box to ask for confirmation.
Destroy the root window only when the user confirms.

**Check:** choosing No leaves the application running; choosing Yes closes it.

### TODO-STAGE1-7 — Update InfoPanel widgets

Implement the three small `InfoPanel` setter methods. Convert numeric values
to label text and delegate the objective mapping to `ObjectivesView`.

**Check:** the setters only update widgets; they do not import, access or alter
the game model.

## 4. Guided optional task

### TODO-STAGE1-6 — Recreate the InfoPanel layout

Using the supplied widgets and image-loading code, arrange moves on the left,
the mascot in the centre, and score/objectives on the right. Preserve
`extension_area`, because Stage 2 will use it for an `IntervalBar`.

This is optional because recreating the full polished panel involves more
layout detail than the core callback and data-flow objectives.

## 5. End-to-end flow to explain

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

## 6. Completion checklist

- The application launches and a complete game can be played.
- Invalid or one-dot selections do not consume a move.
- A valid move updates the board, score, moves and objectives.
- New Game resets model and view state.
- Exit confirmation handles both Yes and No correctly.
- No Stage 2 features (`IntervalBar`, special dots, Companion or ActionBar) are
  added to Stage 1.
- No supplied model, board or animation implementation is deleted or changed.

## 7. Suggested validation

Run the automated tests from the repository root:

```powershell
python -m pytest stage1/tests
```

Then run the GUI and complete the manual checks above:

```powershell
python stage1/a3.py
```
