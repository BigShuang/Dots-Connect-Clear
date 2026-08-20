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
    root.mainloop()


if __name__ == "__main__":
    main()
