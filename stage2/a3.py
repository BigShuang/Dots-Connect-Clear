"""Executable entry point for the Stage 2 game."""

import tkinter as tk

from app import DotsApp


def main() -> None:
    root = tk.Tk()
    root.title("Dots Connect & Clear — Stage 2")
    root.configure(background="#ffffff")
    root.minsize(540, 690)

    application = DotsApp(root)
    application.pack(fill=tk.BOTH, expand=True)

    # Keep the Stage 1S window-placement behaviour for the extended game.
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
