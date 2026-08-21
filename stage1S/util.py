"""Teacher-provided utility code used by several modules."""

from collections import defaultdict
from pathlib import Path
from typing import Any, Callable, DefaultDict, List


PROJECT_ROOT = Path(__file__).resolve().parent.parent
ASSETS_DIR = PROJECT_ROOT / "assets"


class EventEmitter:
    """A small event/listener helper.

    Students use ``on`` and ``emit`` in Stage 1.  The implementation is
    support code and does not need to be a student TODO.
    """

    def __init__(self) -> None:
        self._listeners: DefaultDict[str, List[Callable[..., Any]]] = defaultdict(list)

    def on(self, event_name: str, listener: Callable[..., Any]) -> None:
        if listener not in self._listeners[event_name]:
            self._listeners[event_name].append(listener)

    def emit(self, event_name: str, *args: Any) -> None:
        for listener in tuple(self._listeners[event_name]):
            listener(*args)
