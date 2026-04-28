from __future__ import annotations

from dataclasses import dataclass


MOD_ALIASES = {
    "control": "ctrl",
    "ctl": "ctrl",
    "option": "alt",
    "windows": "win",
    "command": "win",
}

ORDER = ["ctrl", "alt", "shift", "win"]


@dataclass(frozen=True)
class NormalizedHotkey:
    value: str


def normalize_hotkey(text: str) -> NormalizedHotkey:
    raw = text.strip().lower().replace(" ", "")
    if not raw:
        raise ValueError("hotkey is empty")

    parts = [p for p in raw.replace("-", "+").split("+") if p]
    if not parts:
        raise ValueError("hotkey is invalid")

    mapped = [MOD_ALIASES.get(p, p) for p in parts]
    mods = [p for p in mapped if p in ORDER]
    keys = [p for p in mapped if p not in ORDER]

    if len(keys) > 1:
        raise ValueError("only one non-modifier key is supported in MVP")

    ordered_mods = [m for m in ORDER if m in mods]
    normalized = "+".join([*ordered_mods, *keys])
    if not normalized:
        raise ValueError("failed to normalize hotkey")

    return NormalizedHotkey(value=normalized)
