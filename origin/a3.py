"""Executable entry point for Dots Connect & Clear."""

from __future__ import annotations

import tkinter as tk

from app import DotsApp


def main() -> None:
    root = tk.Tk()
    root.title("Dots Connect & Clear")
    root.configure(background="#ffffff")
    root.minsize(540, 690)
    app = DotsApp(root)
    app.pack(fill=tk.BOTH, expand=True)
    root.mainloop()


if __name__ == "__main__":
    main()
