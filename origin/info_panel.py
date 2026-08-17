"""Top status panel for moves, mascot, score and goals."""

from __future__ import annotations

import tkinter as tk
from collections.abc import Mapping

from PIL import Image, ImageTk

from util import ASSETS_DIR
from view import ObjectivesView


class InfoPanel(tk.Frame):
    """Three-column panel whose centre remains stable as values change."""

    def __init__(self, master: tk.Misc) -> None:
        super().__init__(
            master,
            background="#ffffff",
            padx=18,
            pady=12,
            highlightbackground="#e9ecef",
            highlightthickness=1,
        )
        self.columnconfigure(0, weight=1, uniform="side_column")
        self.columnconfigure(1, weight=0, minsize=124)
        self.columnconfigure(2, weight=1, uniform="side_column")

        left = tk.Frame(self, background="#ffffff")
        left.grid(row=0, column=0)
        tk.Label(
            left,
            text="MOVES LEFT",
            background="#ffffff",
            foreground="#344054",
            font=("Segoe UI Semibold", 10),
        ).pack(pady=(0, 2))
        self._moves_label = tk.Label(
            left,
            text="0",
            width=3,
            anchor="center",
            background="#ffffff",
            foreground="#101828",
            font=("Segoe UI Semibold", 48),
        )
        self._moves_label.pack()

        companion = tk.Frame(self, background="#ffffff")
        companion.grid(row=0, column=1)
        source = Image.open(ASSETS_DIR / "pi.png").convert("RGB")
        source.thumbnail((100, 116), resample=Image.Resampling.LANCZOS)
        self._companion_image = ImageTk.PhotoImage(source)
        tk.Label(
            companion,
            image=self._companion_image,
            background="#ffffff",
            borderwidth=0,
        ).pack()

        # Keep both side columns compact so the status panel does not widen
        # the whole application and leave empty bands beside the square board.
        right = tk.Frame(self, width=190, height=140, background="#ffffff")
        right.grid(row=0, column=2)
        right.pack_propagate(False)
        score_row = tk.Frame(right, background="#ffffff")
        score_row.pack(fill=tk.X, padx=(10, 0), pady=(0, 7))
        tk.Label(
            score_row,
            text="SCORE",
            background="#ffffff",
            foreground="#344054",
            font=("Segoe UI Semibold", 10),
        ).pack(side=tk.LEFT, padx=(0, 8))
        self._score_label = tk.Label(
            score_row,
            text="0",
            width=6,
            # Keep a fixed-width score slot so digit changes never resize the
            # panel, but grow the number from the label instead of pushing a
            # short value to the far-right edge.
            anchor="w",
            background="#ffffff",
            foreground="#187ffc",
            font=("Segoe UI Semibold", 26),
        )
        self._score_label.pack(side=tk.LEFT)

        self.objectives_view = ObjectivesView(right)
        self.objectives_view.pack(fill=tk.X, padx=(10, 0))

    def set_score(self, score: int) -> None:
        self._score_label.configure(text=str(score))

    def set_moves_remaining(self, moves: int) -> None:
        self._moves_label.configure(text=str(moves))

    def set_objectives(self, objectives: Mapping[str, int]) -> None:
        self.objectives_view.set_objectives(objectives)
