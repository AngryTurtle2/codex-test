from __future__ import annotations

import threading
import tkinter as tk
from tkinter import messagebox

try:
    import keyboard
except Exception:  # pragma: no cover - optional runtime dependency behavior
    keyboard = None


class GlobalSummon:
    """Mode A: global hotkey summon helper using keyboard package."""

    def __init__(self, root: tk.Tk, combo: str = "ctrl+alt+k") -> None:
        self.root = root
        self.combo = combo
        self._active = False

    def start(self) -> None:
        if keyboard is None:
            messagebox.showwarning("Global hotkey unavailable", "keyboard package is not available.")
            return
        if self._active:
            return

        self._active = True

        def worker() -> None:
            keyboard.add_hotkey(self.combo, self._summon)
            keyboard.wait()

        thread = threading.Thread(target=worker, daemon=True)
        thread.start()

    def _summon(self) -> None:
        self.root.after(0, self._show)

    def _show(self) -> None:
        self.root.deiconify()
        self.root.lift()
        self.root.focus_force()
