"""Application controller that connects the Stage 1 model and views."""

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

        # TODO-STAGE1-1 (GUI composition): identify the two main child widgets
        # of DotsApp, create them with the correct parent, and lay them out so
        # the information panel stays above an expanding game board.  In the
        # student starter, only these construction/layout statements should be
        # replaced; the supplied game and animation code must remain intact.
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
        # TODO-STAGE1-4 (menu callbacks): create a File menu whose commands call
        # new_game and confirm_exit, and attach it to the root window.  Keep the
        # existing controller methods as support code; this task is about menu
        # construction and callback wiring, not reimplementing game reset.
        menu_bar = tk.Menu(self.master)
        file_menu = tk.Menu(menu_bar, tearoff=False)
        file_menu.add_command(label="New Game", command=self.new_game, accelerator="Ctrl+N")
        file_menu.add_separator()
        file_menu.add_command(label="Exit", command=self.confirm_exit)
        menu_bar.add_cascade(label="File", menu=file_menu)
        self.master.configure(menu=menu_bar)

    # TODO-STAGE1-2 (event callbacks): connect the GridView press/drag/release
    # callbacks to the controller, then subscribe redraw/status/reset handlers
    # to the model events.  Do not add game rules here: each callback should
    # delegate to one of the already supplied controller methods.
    def _bind_events(self) -> None:
        self.grid_view.on_press = self.start_connection
        self.grid_view.on_drag = self.continue_connection
        self.grid_view.on_release = self.finish_connection
        self.game.on("selection_changed", self.grid_view.redraw)
        self.game.on("move_completed", self._move_completed)
        self.game.on("reset", self._game_reset)

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
        """Remove dots in the model, then animate surviving dots downward."""
        self.game.remove_pending()
        before_fall = self.grid_view.snapshot()
        self.game.fall_pending()
        self.grid_view.animate_fall(before_fall, self._after_fall)

    def _after_fall(self) -> None:
        """Create replacement dots and animate them in from above the board."""
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

    # TODO-STAGE1-3 (model/view refresh): read score, moves_remaining and
    # objectives from the model's public state and pass them to InfoPanel's
    # setters.  This method must display state only and must not change it.
    def refresh_status(self) -> None:
        self.info_panel.set_score(self.game.score)
        self.info_panel.set_moves_remaining(self.game.moves_remaining)
        self.info_panel.set_objectives(self.game.objectives)

    def new_game(self) -> None:
        self.grid_view.cancel_animation()
        self.game.abort_resolution()
        self._input_locked = False
        self.game.reset()

    def confirm_exit(self) -> None:
        # TODO-STAGE1-5 (dialog): ask the user to confirm before destroying the
        # root window.  The application must remain open when the answer is No.
        if messagebox.askyesno("Exit", "Are you sure you want to quit?"):
            self.master.destroy()

    def _show_result_if_needed(self) -> None:
        if self.game.won:
            messagebox.showinfo("Game Over", "You completed every goal!")
        elif self.game.lost:
            messagebox.showinfo("Game Over", "No moves remain. Try again!")
