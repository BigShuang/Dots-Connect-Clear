"""A segmented Tkinter progress bar for companion charge."""

import tkinter as tk


class IntervalBar(tk.Canvas):
    def __init__(self, master: tk.Misc, steps: int = 6, **kwargs: object) -> None:
        if steps <= 0:
            raise ValueError("steps must be positive")
        super().__init__(master, height=16, background="#ffffff",
                         highlightthickness=0, **kwargs)
        self.steps = steps
        self.progress = 0
        self.bind("<Configure>", lambda _event: self.redraw())

    def set_progress(self, value: int, steps: int = None) -> None:
        if steps is not None:
            if steps <= 0:
                raise ValueError("steps must be positive")
            self.steps = steps
        self.progress = max(0, min(self.steps, int(value)))
        self.redraw()

    def reset(self) -> None:
        self.set_progress(0)

    def redraw(self) -> None:
        self.delete("all")
        width, height = self.winfo_width(), self.winfo_height()
        if width <= 1 or height <= 1:
            return
        usable = width - 2
        self.create_rectangle(1, 1, 1 + usable * self.progress / self.steps,
                              height - 1, fill="#67b7a5", outline="")
        self.create_rectangle(1, 1, width - 1, height - 1, outline="#344054")
        for step in range(1, self.steps):
            x = 1 + usable * step / self.steps
            self.create_line(x, 1, x, height - 1, fill="#344054")
