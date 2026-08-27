"""Executable entry point for the Stage 1 game."""

import tkinter as tk

from app import DotsApp


def main() -> None:
    root = tk.Tk()
    root.title("Dots Connect & Clear — Stage 1")
    root.configure(background="#ffffff")
    root.minsize(540, 690)

    # TODO 1.1 实例化 DotsApp 主应用，并添加到 Tkinter 根窗口，pack() 设置组件自动扩展，占满整个窗口区域
    application = DotsApp(root)
    application.pack(fill=tk.BOTH, expand=True)

    # 等待 Tkinter 计算窗口所需尺寸后，将窗口放到屏幕中央。
    root.update_idletasks()
    window_width = max(root.winfo_reqwidth(), 540)
    window_height = max(root.winfo_reqheight(), 690)
    x_position = (root.winfo_screenwidth() - window_width) // 2
    y_position = (root.winfo_screenheight() - window_height) // 4
    root.geometry(
        f"{window_width}x{window_height}+{x_position}+{y_position}"
    )

    root.mainloop()


if __name__ == "__main__":
    main()
