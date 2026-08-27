"""Application controller for the Stage 2 polymorphic game."""

import tkinter as tk
from tkinter import messagebox
from typing import Optional

from cell import Position
from game import DotGame, MoveResult
from info_panel import InfoPanel
from view import GridView


class DotsApp(tk.Frame):
    """Coordinate widgets and game state; do not implement game rules here."""

    def __init__(self, master: tk.Tk, game: Optional[DotGame] = None) -> None:
        super().__init__(master, background="#ffffff")
        self.master = master
        self.game = game if game is not None else DotGame()
        self._input_locked = False

        self.info_panel = InfoPanel(self)
        self.info_panel.pack(fill=tk.X)
        self.grid_view = GridView(self, self.game)
        self.grid_view.pack(fill=tk.BOTH, expand=True, padx=12, pady=(0, 12))

        self._create_menu()
        self._bind_events()
        self.master.protocol("WM_DELETE_WINDOW", self.confirm_exit)
        self.master.bind("<Control-n>", lambda _event: self.new_game())
        self.refresh_status()
        self.grid_view.redraw()

    def _create_menu(self) -> None:
        menu_bar = tk.Menu(self.master)
        file_menu = tk.Menu(menu_bar, tearoff=False)
        file_menu.add_command(label="New Game", command=self.new_game, accelerator="Ctrl+N")
        file_menu.add_separator()
        file_menu.add_command(label="Exit", command=self.confirm_exit)
        menu_bar.add_cascade(label="File", menu=file_menu)
        self.master.configure(menu=menu_bar)

    # TODO-CANDIDATE (Stage 1 — callbacks): this method is a compact exercise
    # in connecting view events and model events to controller methods.
    def _bind_events(self) -> None:
        self.grid_view.on_press = self.start_connection
        self.grid_view.on_drag = self.continue_connection
        self.grid_view.on_release = self.finish_connection
        self.game.on("selection_changed", self.grid_view.redraw)
        self.game.on("move_completed", self._move_completed)
        self.game.on("reset", self._game_reset)
        self.game.on("companion_changed", self._companion_changed)

    def start_connection(self, position: Position) -> None:
        if not self._input_locked:
            self.game.start_selection(position)

    def continue_connection(self, position: Position) -> None:
        if not self._input_locked:
            self.game.extend_selection(position)

    def finish_connection(self) -> None:
        if self._input_locked:
            return
        pending = self.game.begin_resolution()
        if pending is None:
            return
        self._input_locked = True
        self.grid_view.animate_removal(pending.positions, self._after_removal)

    def _after_removal(self) -> None:
        self.game.remove_pending()
        before_fall = self.grid_view.snapshot()
        self.game.fall_pending()
        self.grid_view.animate_fall(before_fall, self._after_fall)

    def _after_fall(self) -> None:
        previous_ids = set(self.grid_view.snapshot())
        self.game.fill_pending()
        self.grid_view.animate_fill(previous_ids, self._animation_complete)

    def _animation_complete(self) -> None:
        self._input_locked = False
        self.grid_view.redraw()
        self._show_result_if_needed()

    def _move_completed(self, _result: MoveResult) -> None:
        self.refresh_status()

    def _game_reset(self) -> None:
        self.grid_view.redraw()
        self.refresh_status()

    def _companion_changed(self, _charge: int, _activations: int) -> None:
        self.refresh_status()

    # TODO-CANDIDATE (Stage 1 — model/view coordination): students could
    # update all status widgets by using only the model's public attributes.
    def refresh_status(self) -> None:
        self.info_panel.set_score(self.game.score)
        self.info_panel.set_moves_remaining(self.game.moves_remaining)
        self.info_panel.set_objectives(self.game.objectives)
        companion = self.game.companion
        self.info_panel.set_companion_charge(
            companion.charge if companion is not None else 0,
            companion.charge_limit if companion is not None else 6,
            enabled=companion is not None,
        )

    def new_game(self) -> None:
        self.grid_view.cancel_animation()
        self.game.abort_resolution()
        self._input_locked = False
        self.game.reset()

    def confirm_exit(self) -> None:
        if messagebox.askyesno(
            "Exit",
            "Are you sure you want to quit?",
            parent=self.master,
        ):
            self.master.destroy()

    def _show_result_if_needed(self) -> None:
        if self.game.won:
            messagebox.showinfo(
                "Game Over",
                "You completed every goal!",
                parent=self.master,
            )
        elif self.game.lost:
            messagebox.showinfo(
                "Game Over",
                "No moves remain. Try again!",
                parent=self.master,
            )
