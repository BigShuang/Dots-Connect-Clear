"""Executable entry point for the Stage 1 game."""

import tkinter as tk

from app import DotsApp


def main() -> None:
    root = tk.Tk()
    root.title("Dots Connect & Clear — Stage 1")
    root.configure(background="#ffffff")
    root.minsize(540, 690)

    # TODO 1.1 实例化 DotsApp 主应用，并添加到 Tkinter 根窗口，pack() 设置组件自动扩展，占满整个窗口区域

    root.mainloop()


if __name__ == "__main__":
    main()
