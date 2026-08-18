"""Main Tkinter controller for the stage 0-5 application."""

from __future__ import annotations

import tkinter as tk
from tkinter import messagebox

from cell import Position
from game import CompanionGame, DotGame, MoveResult
from info_panel import InfoPanel
from view import GridView


class DotsApp(tk.Frame):
    """Coordinate the model and Tkinter views."""

    def __init__(self, master: tk.Tk, game: DotGame | None = None) -> None:
        super().__init__(master, background="#ffffff")
        self.master = master
        self.game = game or CompanionGame()
        self._result_announced = False
        self._input_locked = False
        self._resolution_job: str | None = None

        self.info_panel = InfoPanel(self)
        self.info_panel.pack(fill=tk.X)
        self.grid_view = GridView(self, self.game)
        self.grid_view.pack(fill=tk.BOTH, expand=True, padx=12, pady=(0, 12))

        self._configure_window_actions()
        self._bind_events()
        self._refresh_status()
        self.grid_view.redraw()

    def _configure_window_actions(self) -> None:
        """Configure the Task 2 game choices, shortcut, and close handling."""
        menu = tk.Menu(self.master)
        file_menu = tk.Menu(menu, tearoff=False)
        file_menu.add_command(label="New Game with Companion", command=lambda: self.new_game(True))
        file_menu.add_command(label="New Game without Companion", command=lambda: self.new_game(False))
        file_menu.add_separator()
        file_menu.add_command(label="Exit", command=self.confirm_exit)
        menu.add_cascade(label="File", menu=file_menu)
        self.master.configure(menu=menu)
        self.master.bind("<Control-n>", lambda _event: self.new_game(isinstance(self.game, CompanionGame)))
        self.master.protocol("WM_DELETE_WINDOW", self.confirm_exit)

    def _bind_events(self) -> None:
        self.grid_view.on_press = self._start_connection
        self.grid_view.on_drag = self._continue_connection
        self.grid_view.on_release = self._finish_connection
        self.game.on("selection_changed", self.grid_view.redraw)
        self.game.on("move_completed", self._move_completed)
        self.game.on("reset", self._game_reset)
        for phase in ("activate", "remove", "fall", "fill"):
            self.game.on(phase, lambda *_args: self.grid_view.redraw())
        self.game.on("companion_changed", self._companion_changed)

    def _start_connection(self, position: Position) -> None:
        if not self._input_locked:
            self.game.start_selection(position)

    def _continue_connection(self, position: Position) -> None:
        if not self._input_locked:
            self.game.extend_selection(position)

    def _finish_connection(self) -> None:
        if self._input_locked or self.game.begin_resolution() is None:
            return
        self._input_locked = True
        self._schedule_phase(self.game.activate_pending)

    def _schedule_phase(self, phase: object) -> None:
        self._resolution_job = self.after(120, lambda: self._run_phase(phase))

    def _run_phase(self, phase: object) -> None:
        """Run one model phase and enqueue the next without blocking Tk."""
        try:
            phase()  # type: ignore[operator]
            if phase == self.game.activate_pending:
                next_phase = self.game.remove_pending
            elif phase == self.game.remove_pending:
                next_phase = self.game.fall_pending
            elif phase == self.game.fall_pending:
                next_phase = self.game.fill_pending
            else:
                self._resolution_job = None
                self._input_locked = False
                return
            self._schedule_phase(next_phase)
        except Exception:
            self._resolution_job = None
            self.game.abort_resolution()
            self._input_locked = False
            self.grid_view.redraw()
            self._refresh_status()
            raise

    def _move_completed(self, _result: MoveResult) -> None:
        self.grid_view.redraw()
        self._refresh_status()
        self.after_idle(self._announce_result_if_needed)

    def _companion_changed(self, _charge: int, _activations: int) -> None:
        self._refresh_status()

    def _game_reset(self) -> None:
        self._result_announced = False
        self.grid_view.redraw()
        self._refresh_status()

    def _refresh_status(self) -> None:
        self.info_panel.set_score(self.game.score)
        self.info_panel.set_moves_remaining(self.game.moves_remaining)
        self.info_panel.set_objectives(self.game.objectives)
        companion = getattr(self.game, "companion", None)
        self.info_panel.set_companion_charge(
            companion.charge if companion is not None else 0,
            companion.charge_limit if companion is not None else 6,
        )

    def new_game(self, with_companion: bool | None = None) -> None:
        if self._resolution_job is not None:
            self.after_cancel(self._resolution_job)
            self._resolution_job = None
        self.game.abort_resolution()
        self._input_locked = False
        requested = isinstance(self.game, CompanionGame) if with_companion is None else with_companion
        if requested == isinstance(self.game, CompanionGame):
            self.game.reset()
            return
        self.game = CompanionGame() if requested else DotGame()
        self.grid_view.game = self.game
        self._bind_events()
        self._game_reset()

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
