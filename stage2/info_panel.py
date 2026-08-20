"""Score, moves, objectives, and Stage 2 companion charge panel."""

import tkinter as tk
from collections.abc import Mapping

from PIL import Image, ImageTk

from util import ASSETS_DIR
from view import ObjectivesView
from interval_bar import IntervalBar


class InfoPanel(tk.Frame):
    """Display game information without reading or changing the model."""

    def __init__(self, master: tk.Misc) -> None:
        super().__init__(
            master,
            background="#ffffff",
            padx=18,
            pady=12,
            highlightbackground="#e4e7ec",
            highlightthickness=1,
        )
        self.columnconfigure(0, weight=1, uniform="side")
        self.columnconfigure(1, weight=0, minsize=124)
        self.columnconfigure(2, weight=1, uniform="side")

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
            background="#ffffff",
            foreground="#101828",
            font=("Segoe UI Semibold", 48),
        )
        self._moves_label.pack()

        centre = tk.Frame(self, background="#ffffff")
        centre.grid(row=0, column=1)
        source = Image.open(ASSETS_DIR / "pi.png").convert("RGB")
        source.thumbnail((100, 116), Image.Resampling.LANCZOS)
        self._mascot_image = ImageTk.PhotoImage(source)
        tk.Label(
            centre,
            image=self._mascot_image,
            background="#ffffff",
            borderwidth=0,
        ).pack()

        # Stage 2 extension point: an IntervalBar can be packed in this frame
        # without changing the surrounding three-column layout.
        self.extension_area = tk.Frame(centre, background="#ffffff")
        self.extension_area.pack(fill=tk.X)
        tk.Label(self.extension_area, text="COMPANION CHARGE",
                 background="#ffffff", foreground="#344054",
                 font=("Segoe UI Semibold", 8)).pack()
        self.interval_bar = IntervalBar(self.extension_area, steps=6, width=106)
        self.interval_bar.pack(pady=(2, 0))

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
            anchor="w",
            background="#ffffff",
            foreground="#187ffc",
            font=("Segoe UI Semibold", 26),
        )
        self._score_label.pack(side=tk.LEFT)

        self.objectives_view = ObjectivesView(right)
        self.objectives_view.pack(fill=tk.X, padx=(10, 0))

    # TODO-CANDIDATE (Stage 1 — widget state): students could implement the
    # three setters below after the labels have been supplied.
    def set_score(self, score: int) -> None:
        self._score_label.configure(text=str(score))

    def set_moves_remaining(self, moves: int) -> None:
        self._moves_label.configure(text=str(moves))

    def set_objectives(self, objectives: Mapping[str, int]) -> None:
        self.objectives_view.set_objectives(objectives)

    def set_companion_charge(
        self, charge: int, limit: int = 6, enabled: bool = True
    ) -> None:
        for child in self.extension_area.winfo_children():
            if isinstance(child, tk.Label):
                child.configure(text="COMPANION CHARGE" if enabled else "NO COMPANION")
        self.interval_bar.set_progress(charge, limit)
