"""Small shared utilities for the Dots project."""

from __future__ import annotations

from collections import defaultdict
from pathlib import Path
from typing import Any, Callable


PROJECT_ROOT = Path(__file__).resolve().parent.parent
ASSETS_DIR = PROJECT_ROOT / "assets"


class EventEmitter:
    """A minimal observer implementation used by the model and controller."""

    def __init__(self) -> None:
        self._listeners: dict[str, list[Callable[..., Any]]] = defaultdict(list)

    def on(self, event: str, listener: Callable[..., Any]) -> None:
        """Register *listener* for *event*."""
        if listener not in self._listeners[event]:
            self._listeners[event].append(listener)

    def emit(self, event: str, *args: Any, **kwargs: Any) -> None:
        """Call all listeners currently registered for *event*."""
        for listener in tuple(self._listeners[event]):
            listener(*args, **kwargs)

