# Stage 1 — Basic Game

This folder contains the complete teacher implementation for Stage 1.

Run from the repository root:

```powershell
pip install -r stage1/requirements.txt
python stage1/a3.py
```

Stage 1 includes the complete basic game, `DotsApp`, `InfoPanel`, menu and
dialogs. It intentionally does not include `IntervalBar`, special dots,
companions, or `ActionBar`.

The comments marked `TODO-CANDIDATE` identify possible future student
exercises. They do not remove any implementation, so this version remains
fully runnable.

The removal, gravity, and refill animations are complete teacher support code.
Students are not expected to implement or call the animation controller. The
model still provides synchronous `finish_selection()` for tests, while the GUI
uses non-blocking Tkinter `after()` frames to shrink removed dots, slide
surviving dots downward, and drop replacement dots in from above.

Stage 2 can extend this version through `AbstractDot`, `DotFactory`, the
`factory` argument of `DotGame`, `AbstractDot.asset_family`, and the reserved
`InfoPanel.extension_area` without rewriting the Stage 1 game flow. The
default `AbstractDot.activate` hook is already called during move resolution,
so a Stage 2 dot can add a local effect by overriding that method.
