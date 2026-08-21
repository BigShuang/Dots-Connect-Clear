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

        # TODO 2.4 创建 InfoPanel 并将它放在应用顶部。
        self.info_panel = InfoPanel(self)
        self.info_panel.pack(fill=tk.X)

        # TODO 1.2 使用 pack 设置 GridView 布局：
        # 使棋盘区域占满窗口剩余空间，并在窗口缩放时保持自适应，同时设置合适的边距
        self.grid_view = GridView(self, self.game)
        self.grid_view.pack(fill=tk.BOTH, expand=True, padx=12, pady=(0, 12))
        self._bind_events()

        # TODO 3.1 初始化 File 菜单，
        self._create_menu()
        # 注册窗口关闭协议和 New Game 快捷键。
        self.master.protocol("WM_DELETE_WINDOW", self.confirm_exit)
        self.master.bind("<Control-n>", lambda _event: self.new_game())

        # 2.7 在 InfoPanel 创建完成后显示模型的初始状态。
        self.refresh_status()

        self.grid_view.redraw()

    # TODO 3.2 创建 File 菜单，将菜单命令分别连接到 new_game 和 confirm_exit，
    # 并把菜单栏设置到根窗口。本任务只练习菜单创建和回调绑定，不需要
    # 重新实现已经提供的游戏重置逻辑。
    def _create_menu(self) -> None:
        menu_bar = tk.Menu(self.master)
        file_menu = tk.Menu(menu_bar, tearoff=False)
        file_menu.add_command(label="New Game", command=self.new_game, accelerator="Ctrl+N")
        file_menu.add_separator()
        file_menu.add_command(label="Exit", command=self.confirm_exit)
        menu_bar.add_cascade(label="File", menu=file_menu)
        self.master.configure(menu=menu_bar)

    def _bind_events(self) -> None:
        # 将 GridView 的按下、拖动和释放回调连接到控制器方法，并让选择变化触发棋盘重绘。
        self.grid_view.on_press = self.start_connection
        self.grid_view.on_drag = self.continue_connection
        self.grid_view.on_release = self.finish_connection
        self.game.on("selection_changed", self.grid_view.redraw)

        # 2.5 将回合完成和游戏重置事件连接到 InfoPanel 状态刷新流程。
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

    # TODO 2.6 更新游戏状态显示：
    # 从 game 获取 score、moves_remaining 和 objectives 等状态信息，
    # 并传递给 InfoPanel 对应方法进行显示更新
    # 本方法只负责同步界面显示，不修改游戏状态
    def refresh_status(self) -> None:
        self.info_panel.set_score(self.game.score)
        self.info_panel.set_moves_remaining(self.game.moves_remaining)
        self.info_panel.set_objectives(self.game.objectives)

    def new_game(self) -> None:
        # 3.3 实现 File > New Game 所需的重置操作，并确保未完成的动画和
        # 结算状态不会带入新游戏。
        self.grid_view.cancel_animation()
        self.game.abort_resolution()
        self._input_locked = False
        self.game.reset()

    # TODO 3.4 在销毁根窗口前使用对话框询问用户是否确认退出；用户选择 No 时，
    # 应用程序必须继续运行。
    def confirm_exit(self) -> None:
        if messagebox.askyesno("Exit", "Are you sure you want to quit?"):
            self.master.destroy()

    # TODO 3.5 游戏结束后，根据模型的 won/lost 状态显示对应结果弹窗。
    # 弹窗只负责通知结果，不能在这里重新判断目标或剩余步数规则。
    def _show_result_if_needed(self) -> None:

        if self.game.won:
            messagebox.showinfo("Game Over", "You completed every goal!")
        elif self.game.lost:
            messagebox.showinfo("Game Over", "No moves remain. Try again!")
