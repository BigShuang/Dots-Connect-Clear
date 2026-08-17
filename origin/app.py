"""Main Tkinter controller for the stage 0-5 application."""

from __future__ import annotations

import tkinter as tk
from tkinter import messagebox

from cell import Position
from game import DotGame, MoveResult
from info_panel import InfoPanel
from view import GridView


class DotsApp(tk.Frame):
    """Coordinate the model and Tkinter views."""

    def __init__(self, master: tk.Tk, game: DotGame | None = None) -> None:
        super().__init__(master, background="#ffffff")
        self.master = master
        self.game = game or DotGame()
        self._result_announced = False

        self.info_panel = InfoPanel(self)
        self.info_panel.pack(fill=tk.X)
        self.grid_view = GridView(self, self.game)
        self.grid_view.pack(fill=tk.BOTH, expand=True, padx=12, pady=(0, 12))

        self._configure_window_actions()
        self._bind_events()
        self._refresh_status()
        self.grid_view.redraw()

    def _configure_window_actions(self) -> None:
        """Keep window shortcuts and close handling without a visible menu bar."""
        self.master.bind("<Control-n>", lambda _event: self.new_game())
        self.master.protocol("WM_DELETE_WINDOW", self.confirm_exit)

    def _bind_events(self) -> None:
        self.grid_view.on_press = self._start_connection
        self.grid_view.on_drag = self._continue_connection
        self.grid_view.on_release = self._finish_connection
        self.game.on("selection_changed", self.grid_view.redraw)
        self.game.on("move_completed", self._move_completed)
        self.game.on("reset", self._game_reset)

    def _start_connection(self, position: Position) -> None:
        self.game.start_selection(position)

    def _continue_connection(self, position: Position) -> None:
        self.game.extend_selection(position)

    def _finish_connection(self) -> None:
        self.game.finish_selection()

    def _move_completed(self, _result: MoveResult) -> None:
        self.grid_view.redraw()
        self._refresh_status()
        self.after_idle(self._announce_result_if_needed)

    def _game_reset(self) -> None:
        self._result_announced = False
        self.grid_view.redraw()
        self._refresh_status()

    def _refresh_status(self) -> None:
        self.info_panel.set_score(self.game.score)
        self.info_panel.set_moves_remaining(self.game.moves_remaining)
        self.info_panel.set_objectives(self.game.objectives)

    def new_game(self) -> None:
        self.game.reset()

    def confirm_exit(self) -> None:
        if messagebox.askyesno("Exit Dots", "Are you sure you want to quit?"):
            self.master.destroy()

    def _announce_result_if_needed(self) -> None:
        if self._result_announced or not self.game.is_over:
            return
        self._result_announced = True
        if self.game.won:
            messagebox.showinfo(
                "You won!",
                f"All objectives cleared. Final score: {self.game.score}",
            )
        else:
            messagebox.showinfo(
                "Game over",
                f"No moves remaining. Final score: {self.game.score}",
            )
