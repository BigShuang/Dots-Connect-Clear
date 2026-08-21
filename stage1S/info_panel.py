"""The Stage 1 score, moves, mascot, and objectives panel."""

import tkinter as tk
from collections.abc import Mapping

from PIL import Image, ImageTk

from util import ASSETS_DIR
from view import ObjectivesView


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

        # TODO 2.1 创建并布局步数显示区域， 添加标题和数字标签，用于展示游戏当前剩余步数。
        # 设置白色背景、黑色字体，font=("Segoe UI Semibold", size) 中 size 根据显示效果调整
        # 使用 pack() 完成组件布局
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

        # 中间放核心素材图片作为游戏界面标识
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

        # Code for Stage 2 extension point: an IntervalBar can be packed in this frame
        # without changing the surrounding three-column layout.
        self.extension_area = tk.Frame(centre, background="#ffffff")
        self.extension_area.pack(fill=tk.X)

        right = tk.Frame(self, width=190, height=140, background="#ffffff")
        right.grid(row=0, column=2)
        right.pack_propagate(False)
        score_row = tk.Frame(right, background="#ffffff")
        score_row.pack(fill=tk.X, padx=(10, 0), pady=(0, 7))

        # TODO 2.2 创建并布局分数信息：添加 SCORE 标题和数字标签，用于展示游戏当前得分
        # 设置文字样式，并使用 pack() 将标签水平排列显示
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

    # TODO 2.3 更新已经提供的分数与剩余步数Label
    def set_score(self, score: int) -> None:
        self._score_label.configure(text=str(score))

    def set_moves_remaining(self, moves: int) -> None:
        self._moves_label.configure(text=str(moves))

    def set_objectives(self, objectives: Mapping[str, int]) -> None:
        self.objectives_view.set_objectives(objectives)
