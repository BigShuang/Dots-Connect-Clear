"""A segmented Tkinter progress bar."""

from __future__ import annotations

import tkinter as tk


class IntervalBar(tk.Canvas):
    """Display an integer progress value split into equal visual steps."""

    def __init__(self, master: tk.Misc, steps: int = 6, **kwargs: object) -> None:
        if steps <= 0:
            raise ValueError("steps must be positive")
        super().__init__(
            master,
            height=18,
            background="#ffffff",
            highlightthickness=0,
            **kwargs,
        )
        self.steps = steps
        self.progress = 0
        self.bind("<Configure>", lambda _event: self.redraw())

    def set_progress(self, value: int) -> None:
        self.progress = max(0, min(self.steps, int(value)))
        self.redraw()

    def reset(self) -> None:
        self.set_progress(0)

    def redraw(self) -> None:
        self.delete("all")
        width, height = self.winfo_width(), self.winfo_height()
        if width <= 1 or height <= 1:
            return
        inset = 1
        usable = max(0, width - inset * 2)
        self.create_rectangle(
            inset,
            inset,
            inset + usable * self.progress / self.steps,
            height - inset,
            fill="#67b7a5",
            outline="",
        )
        self.create_rectangle(inset, inset, width - inset, height - inset, outline="#344054")
        for step in range(1, self.steps):
            x = inset + usable * step / self.steps
            self.create_line(x, inset, x, height - inset, fill="#344054")
