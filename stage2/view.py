"""Tkinter views for the Stage 1 game."""

import tkinter as tk
from collections.abc import Mapping
from pathlib import Path
from typing import Callable, Dict, List, Optional, Set, Tuple

from PIL import Image, ImageTk

from cell import Position
from dot import AbstractDot
from game import DotGame
from util import ASSETS_DIR


DOT_COLOURS = {
    "coral": "#a30e15",
    "blue": "#508ebf",
    "gold": "#f9bf3b",
    "purple": "#493047",
}


def dot_asset_path(dot: AbstractDot) -> Path:
    """Return the image path through the dot's stable public interface."""
    if dot.asset_family in {"wildcard", "shell", "turtle", "anchor"}:
        return ASSETS_DIR / "dots" / (dot.asset_family + ".png")
    if dot.asset_family == "beam":
        return (ASSETS_DIR / "dots" / "beam" / str(dot.asset_variant) /
                (dot.kind + ".png"))
    return ASSETS_DIR / "dots" / dot.asset_family / (dot.kind + ".png")


class GridView(tk.Canvas):
    """Draw the board and translate mouse input into board positions."""

    def __init__(self, master: tk.Misc, game: DotGame, **kwargs: object) -> None:
        defaults = {
            "background": "#ffffff",
            "highlightthickness": 0,
            "width": 510,
            "height": 510,
        }
        defaults.update(kwargs)
        super().__init__(master, **defaults)
        self.game = game
        self.on_press: Optional[Callable[[Position], None]] = None
        self.on_drag: Optional[Callable[[Position], None]] = None
        self.on_release: Optional[Callable[[], None]] = None
        self._last_drag_position: Optional[Position] = None
        self._source_images: Dict[Tuple[str, str, str], Image.Image] = {}
        self._dot_images: Dict[Tuple[str, str, str, int], ImageTk.PhotoImage] = {}
        self._animation_job: Optional[str] = None
        self._hidden_dot_ids: Set[int] = set()
        self._animated_dots: List[Tuple[AbstractDot, float, float, float]] = []

        self.bind("<Configure>", lambda _event: self.redraw())
        self.bind("<Button-1>", self._handle_press)
        self.bind("<B1-Motion>", self._handle_drag)
        self.bind("<ButtonRelease-1>", self._handle_release)

    def set_game(self, game: DotGame) -> None:
        self.game = game
        self.redraw()

    def redraw(self) -> None:
        self.delete("all")
        geometry = self._geometry()
        if geometry is None:
            return
        cell_size, left, top = geometry
        selected = set(self.game.selection)

        # Match the origin game: one continuous dark outline around the board.
        self.create_rectangle(
            left,
            top,
            left + self.game.columns * cell_size,
            top + self.game.rows * cell_size,
            fill="#ffffff",
            outline="#495057",
            width=2,
        )

        # The centre is one warm, outlined area rather than nine separate cells.
        if self.game.grid.blocked_positions:
            blocked_rows = [row for row, _column in self.game.grid.blocked_positions]
            blocked_columns = [
                column for _row, column in self.game.grid.blocked_positions
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
            points = []
            for position in self.game.selection:
                x, y = self._centre(position, cell_size, left, top)
                points.extend((x, y))
            self.create_line(
                *points,
                fill=DOT_COLOURS.get(self.game.selection_kind or "", "#495057"),
                width=max(6, cell_size * 0.14),
                capstyle=tk.ROUND,
                joinstyle=tk.ROUND,
            )

        for position in self.game.grid.positions():
            dot = self.game.grid.dot_at(position)
            if dot is None or id(dot) in self._hidden_dot_ids:
                continue
            x, y = self._centre(position, cell_size, left, top)
            radius = cell_size * (0.34 if position in selected else 0.31)
            diameter = max(2, round(radius * 2))
            self.create_image(x, y, image=self._dot_image(dot, diameter))

        for dot, row, column, scale in self._animated_dots:
            x, y = self._centre((row, column), cell_size, left, top)
            diameter = max(2, round(cell_size * 0.62 * scale))
            self.create_image(x, y, image=self._dot_image(dot, diameter))

        # Same foreground rule as Stage 1: dots can fall through the centre
        # columns, but the block hides the part of their path behind it.
        if self.game.grid.blocked_positions:
            blocked_rows = [row for row, _column in self.game.grid.blocked_positions]
            blocked_columns = [
                column for _row, column in self.game.grid.blocked_positions
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

        # Simulate a clipping region and keep the outer border above all dots.
        canvas_width = self.winfo_width()
        canvas_height = self.winfo_height()
        board_right = left + self.game.columns * cell_size
        board_bottom = top + self.game.rows * cell_size
        mask_options = {"fill": "#ffffff", "outline": ""}
        self.create_rectangle(0, 0, canvas_width, top + 1, **mask_options)
        self.create_rectangle(0, top, left + 1, board_bottom, **mask_options)
        self.create_rectangle(
            board_right - 1, top, canvas_width, board_bottom, **mask_options
        )
        self.create_rectangle(
            0, board_bottom - 1, canvas_width, canvas_height, **mask_options
        )
        self.create_rectangle(
            left, top, board_right, board_bottom,
            fill="", outline="#495057", width=2,
        )

    def snapshot(self) -> Dict[int, Tuple[AbstractDot, Position]]:
        return {
            id(dot): (dot, position)
            for position in self.game.grid.positions()
            if (dot := self.game.grid.dot_at(position)) is not None
        }

    def cancel_animation(self) -> None:
        if self._animation_job is not None:
            self.after_cancel(self._animation_job)
            self._animation_job = None
        self._hidden_dot_ids.clear()
        self._animated_dots.clear()
        self.redraw()

    def animate_removal(
        self, positions: List[Position], on_complete: Callable[[], None]
    ) -> None:
        self.cancel_animation()
        dots = [(dot, position) for position in positions
                if (dot := self.game.grid.dot_at(position)) is not None]
        self._hidden_dot_ids = {id(dot) for dot, _position in dots}

        def frame(progress: float) -> None:
            scale = max(0.05, 1.0 - self._ease(progress))
            self._animated_dots = [
                (dot, position[0], position[1], scale)
                for dot, position in dots
            ]

        self._animate(11, frame, on_complete)

    def animate_fall(
        self, before: Dict[int, Tuple[AbstractDot, Position]],
        on_complete: Callable[[], None],
    ) -> None:
        self.cancel_animation()
        after = self.snapshot()
        moving = []
        for dot_id, (dot, start) in before.items():
            if dot_id in after:
                end = after[dot_id][1]
                if start != end:
                    moving.append((dot_id, dot, start, end))
        self._hidden_dot_ids = {item[0] for item in moving}

        def frame(progress: float) -> None:
            eased = self._ease(progress)
            self._animated_dots = [
                (dot, start[0] + (end[0] - start[0]) * eased,
                 start[1] + (end[1] - start[1]) * eased, 1.0)
                for _dot_id, dot, start, end in moving
            ]

        self._animate(18 if moving else 1, frame, on_complete)

    def animate_fill(
        self, previous_ids: Set[int], on_complete: Callable[[], None]
    ) -> None:
        self.cancel_animation()
        after = self.snapshot()
        entering = [(dot_id, dot, position)
                    for dot_id, (dot, position) in after.items()
                    if dot_id not in previous_ids]
        counts: Dict[int, int] = {}
        for _dot_id, _dot, (_row, column) in entering:
            counts[column] = counts.get(column, 0) + 1
        self._hidden_dot_ids = {item[0] for item in entering}

        def frame(progress: float) -> None:
            eased = self._ease(progress)
            self._animated_dots = []
            for _dot_id, dot, (row, column) in entering:
                start_row = row - counts[column]
                current_row = start_row + (row - start_row) * eased
                self._animated_dots.append((dot, current_row, column, 1.0))

        self._animate(18 if entering else 1, frame, on_complete)

    def _animate(
        self, frames: int, draw_frame: Callable[[float], None],
        on_complete: Callable[[], None],
    ) -> None:
        current = 0

        def tick() -> None:
            nonlocal current
            progress = min(1.0, current / max(1, frames))
            draw_frame(progress)
            self.redraw()
            if current >= frames:
                self._animation_job = None
                self._hidden_dot_ids.clear()
                self._animated_dots.clear()
                on_complete()
                return
            current += 1
            self._animation_job = self.after(16, tick)

        tick()

    @staticmethod
    def _ease(progress: float) -> float:
        return progress * progress * (3.0 - 2.0 * progress)

    def _dot_image(self, dot: AbstractDot, diameter: int) -> ImageTk.PhotoImage:
        family = dot.asset_family
        variant = str(dot.asset_variant or "")
        cache_key = family, variant, dot.kind, diameter
        image = self._dot_images.get(cache_key)
        if image is not None:
            return image

        source_key = family, variant, dot.kind
        source = self._source_images.get(source_key)
        if source is None:
            source = Image.open(dot_asset_path(dot)).convert("RGBA")
            self._source_images[source_key] = source
        resized = source.resize((diameter, diameter), Image.Resampling.LANCZOS)
        image = ImageTk.PhotoImage(resized)
        self._dot_images[cache_key] = image
        return image

    def _geometry(self) -> Optional[Tuple[float, float, float]]:
        width = self.winfo_width()
        height = self.winfo_height()
        if width <= 1 or height <= 1:
            return None
        board_size = min(width, height) * 0.96
        cell_size = board_size / max(self.game.rows, self.game.columns)
        left = (width - self.game.columns * cell_size) / 2
        top = (height - self.game.rows * cell_size) / 2
        return cell_size, left, top

    @staticmethod
    def _centre(
        position: Tuple[float, float], cell_size: float, left: float, top: float
    ) -> Tuple[float, float]:
        row, column = position
        return (
            left + (column + 0.5) * cell_size,
            top + (row + 0.5) * cell_size,
        )

    def _position_at(self, x: float, y: float) -> Optional[Position]:
        geometry = self._geometry()
        if geometry is None:
            return None
        cell_size, left, top = geometry
        row = int((y - top) // cell_size)
        column = int((x - left) // cell_size)
        position = row, column
        if not self.game.grid.in_bounds(position):
            return None
        return position

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
    """A reusable row of objective counters."""

    def __init__(self, master: tk.Misc) -> None:
        super().__init__(master, background="#ffffff")
        tk.Label(
            self,
            text="GOALS",
            background="#ffffff",
            foreground="#344054",
            font=("Segoe UI Semibold", 10),
        ).pack(anchor="w", pady=(0, 4))
        self._row = tk.Frame(self, background="#ffffff")
        self._row.pack(anchor="w")
        self._labels: Dict[str, tk.Label] = {}
        self._icons: Dict[str, ImageTk.PhotoImage] = {}

    def set_objectives(self, objectives: Mapping[str, int]) -> None:
        if tuple(self._labels) != tuple(objectives):
            for widget in self._row.winfo_children():
                widget.destroy()
            self._labels.clear()
            self._icons.clear()
            for column, kind in enumerate(objectives):
                item = tk.Frame(self._row, width=40, height=52, background="#ffffff")
                item.grid(row=0, column=column, padx=1)
                item.grid_propagate(False)
                source = Image.open(
                    ASSETS_DIR / "dots" / "basic" / (kind + ".png")
                ).convert("RGBA")
                icon = ImageTk.PhotoImage(
                    source.resize((22, 22), Image.Resampling.LANCZOS)
                )
                self._icons[kind] = icon
                tk.Label(
                    item, image=icon, background="#ffffff", borderwidth=0
                ).pack()
                label = tk.Label(
                    item,
                    text="0",
                    width=3,
                    anchor="center",
                    background="#ffffff",
                    foreground="#101828",
                    font=("Segoe UI Semibold", 11),
                )
                label.pack()
                self._labels[kind] = label

        for kind, amount in objectives.items():
            self._labels[kind].configure(text=str(amount))
