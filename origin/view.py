"""Tkinter views for the dot grid and objectives."""

from __future__ import annotations

import tkinter as tk
from collections.abc import Callable, Mapping

from PIL import Image, ImageTk

from cell import Position
from game import DotGame
from util import ASSETS_DIR


DOT_COLOURS = {
    "coral": "#a30e15",
    "blue": "#508ebf",
    "gold": "#f9bf3b",
    "purple": "#493047",
}


class GridView(tk.Canvas):
    """Resizable Canvas that renders dots and translates pointer events."""

    def __init__(self, master: tk.Misc, game: DotGame, **kwargs: object) -> None:
        super().__init__(
            master,
            width=510,
            height=510,
            background="#ffffff",
            highlightthickness=0,
            **kwargs,
        )
        self.game = game
        self.on_press: Callable[[Position], None] | None = None
        self.on_drag: Callable[[Position], None] | None = None
        self.on_release: Callable[[], None] | None = None
        self._last_drag_position: Position | None = None
        self._dot_images: dict[tuple[str, int], ImageTk.PhotoImage] = {}
        self._dot_source_images: dict[str, Image.Image] = {}
        self.bind("<Button-1>", self._handle_press)
        self.bind("<B1-Motion>", self._handle_drag)
        self.bind("<ButtonRelease-1>", self._handle_release)
        self.bind("<Configure>", lambda _event: self.redraw())

    def redraw(self) -> None:
        self.delete("all")
        geometry = self._geometry()
        if geometry is None:
            return
        cell_size, left, top = geometry
        selected = set(self.game.selection)
        self.create_rectangle(
            left,
            top,
            left + self.game.columns * cell_size,
            top + self.game.rows * cell_size,
            fill="#ffffff",
            outline="#495057",
            width=2,
        )
        if self.game.grid.blocked_positions:
            blocked_rows = [position[0] for position in self.game.grid.blocked_positions]
            blocked_columns = [
                position[1] for position in self.game.grid.blocked_positions
            ]
            first_row, last_row = min(blocked_rows), max(blocked_rows)
            first_column, last_column = min(blocked_columns), max(blocked_columns)
            self.create_rectangle(
                left + first_column * cell_size,
                top + first_row * cell_size,
                left + (last_column + 1) * cell_size,
                top + (last_row + 1) * cell_size,
                fill="#fceee2",
                outline="#495057",
                width=2,
            )

        if len(self.game.selection) >= 2:
            points: list[float] = []
            for position in self.game.selection:
                x, y = self._centre(position, cell_size, left, top)
                points.extend((x, y))
            colour = DOT_COLOURS.get(self.game.selection_kind or "", "#495057")
            self.create_line(
                *points,
                fill=colour,
                width=max(6, cell_size * 0.14),
                capstyle=tk.ROUND,
                joinstyle=tk.ROUND,
            )

        for position in self.game.grid.positions():
            dot = self.game.grid.dot_at(position)
            if dot is None:
                continue
            centre_x, centre_y = self._centre(position, cell_size, left, top)
            radius = cell_size * (0.34 if position in selected else 0.31)
            diameter = max(2, round(radius * 2))
            self.create_image(
                centre_x,
                centre_y,
                image=self._dot_image(dot.kind, diameter),
            )

    def _dot_image(self, kind: str, diameter: int) -> ImageTk.PhotoImage:
        """Return a cached, high-quality resize of a repository PNG asset."""
        key = kind, diameter
        cached = self._dot_images.get(key)
        if cached is not None:
            return cached

        source = self._dot_source_images.get(kind)
        if source is None:
            asset_path = ASSETS_DIR / "dots" / "basic" / f"{kind}.png"
            source = Image.open(asset_path).convert("RGBA")
            self._dot_source_images[kind] = source
        smooth = source.resize(
            (diameter, diameter),
            resample=Image.Resampling.LANCZOS,
        )
        image = ImageTk.PhotoImage(smooth)
        self._dot_images[key] = image
        return image

    def _geometry(self) -> tuple[float, float, float] | None:
        width = self.winfo_width()
        height = self.winfo_height()
        if width <= 1 or height <= 1:
            return None
        board_size = min(width, height) * 0.96
        cell_size = board_size / max(self.game.rows, self.game.columns)
        return cell_size, (width - self.game.columns * cell_size) / 2, (
            height - self.game.rows * cell_size
        ) / 2

    @staticmethod
    def _centre(
        position: Position, cell_size: float, left: float, top: float
    ) -> tuple[float, float]:
        row, column = position
        return (
            left + (column + 0.5) * cell_size,
            top + (row + 0.5) * cell_size,
        )

    def _position_at(self, x: float, y: float) -> Position | None:
        geometry = self._geometry()
        if geometry is None:
            return None
        cell_size, left, top = geometry
        column = int((x - left) // cell_size)
        row = int((y - top) // cell_size)
        position = row, column
        return position if self.game.grid.in_bounds(position) else None

    def _handle_press(self, event: tk.Event) -> None:
        position = self._position_at(event.x, event.y)
        self._last_drag_position = position
        if position is not None and self.on_press is not None:
            self.on_press(position)

    def _handle_drag(self, event: tk.Event) -> None:
        position = self._position_at(event.x, event.y)
        if position is None or position == self._last_drag_position:
            return
        self._last_drag_position = position
        if self.on_drag is not None:
            self.on_drag(position)

    def _handle_release(self, _event: tk.Event) -> None:
        self._last_drag_position = None
        if self.on_release is not None:
            self.on_release()


class ObjectivesView(tk.Frame):
    """Compact objective counters used by InfoPanel."""

    def __init__(self, master: tk.Misc) -> None:
        super().__init__(master, background="#ffffff")
        tk.Label(
            self,
            text="GOALS",
            background="#ffffff",
            foreground="#344054",
            font=("Segoe UI Semibold", 10),
        ).pack(anchor="w", pady=(0, 4))
        self._labels: dict[str, tk.Label] = {}
        self._icons: dict[str, ImageTk.PhotoImage] = {}
        self._goals_row = tk.Frame(self, background="#ffffff")
        self._goals_row.pack(anchor="w")

    def set_objectives(self, objectives: Mapping[str, int]) -> None:
        if tuple(self._labels) != tuple(objectives):
            for child in self._goals_row.winfo_children():
                child.destroy()
            self._labels.clear()
            self._icons.clear()
            for column, kind in enumerate(objectives):
                goal = tk.Frame(
                    self._goals_row,
                    width=40,
                    height=52,
                    background="#ffffff",
                )
                goal.grid(row=0, column=column, padx=1)
                goal.grid_propagate(False)
                source = Image.open(
                    ASSETS_DIR / "dots" / "basic" / f"{kind}.png"
                ).convert("RGBA")
                icon = ImageTk.PhotoImage(
                    source.resize((22, 22), resample=Image.Resampling.LANCZOS)
                )
                self._icons[kind] = icon
                tk.Label(
                    goal,
                    image=icon,
                    background="#ffffff",
                    borderwidth=0,
                ).pack()
                value = tk.Label(
                    goal,
                    text="0",
                    width=3,
                    anchor="center",
                    background="#ffffff",
                    foreground="#101828",
                    font=("Segoe UI Semibold", 11),
                )
                value.pack()
                self._labels[kind] = value

        for kind, remaining in objectives.items():
            self._labels[kind].configure(text=str(remaining))
