from __future__ import annotations

import ctypes
import ctypes.wintypes
import json
import platform
import subprocess
from dataclasses import dataclass, asdict
from pathlib import Path
from typing import Any

from .hotkey_parser import normalize_hotkey

try:
    import psutil
except Exception:  # pragma: no cover
    psutil = None


@dataclass
class DetectionResult:
    hotkey: str
    owner: str
    action: str
    confidence: int
    evidence: list[str]

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


class HotkeyDetector:
    def __init__(self, rules_file: Path) -> None:
        self.rules = json.loads(rules_file.read_text(encoding="utf-8"))

    def detect(self, hotkey_text: str) -> DetectionResult:
        hk = normalize_hotkey(hotkey_text).value
        evidence: list[str] = []

        system_action = self.rules.get("system_reserved", {}).get(hk)
        if system_action:
            evidence.append("Matched system_reserved knowledge base")
            return DetectionResult(
                hotkey=hk,
                owner="Windows System",
                action=system_action,
                confidence=98,
                evidence=evidence,
            )

        foreground = self._get_foreground_process()
        known_match = self._known_app_hotkey_match(hk)

        if known_match:
            owner, action = known_match
            confidence = 90 if foreground and foreground.lower() == owner.lower() else 78
            evidence.append(f"Matched known app rule: {owner}:{hk}")
            if foreground:
                evidence.append(f"Foreground process observed: {foreground}")
            return DetectionResult(
                hotkey=hk,
                owner=owner,
                action=action,
                confidence=confidence,
                evidence=evidence,
            )

        probe = self._probe_hotkey_registration(hk)
        if not probe["available"]:
            evidence.append("Win32 RegisterHotKey probe failed => likely already captured")
            if foreground:
                evidence.append(f"Foreground process is candidate owner: {foreground}")
            return DetectionResult(
                hotkey=hk,
                owner=foreground or "Unknown process",
                action="Hotkey appears occupied by app/system; action unknown",
                confidence=65 if foreground else 52,
                evidence=evidence,
            )

        evidence.append("Hotkey registration probe succeeded => likely unoccupied globally")
        if foreground:
            evidence.append(f"Foreground process may consume hotkey contextually: {foreground}")
        return DetectionResult(
            hotkey=hk,
            owner=foreground or "No clear owner",
            action="No global owner detected; may be local app shortcut",
            confidence=45 if foreground else 30,
            evidence=evidence,
        )

    def _known_app_hotkey_match(self, hk: str) -> tuple[str, str] | None:
        running = self._running_process_names()
        for exe, mapping in self.rules.get("apps", {}).items():
            if hk in mapping and exe.lower() in running:
                return exe, mapping[hk]
        return None

    def _running_process_names(self) -> set[str]:
        if psutil is not None:
            return {p.info["name"].lower() for p in psutil.process_iter(attrs=["name"]) if p.info.get("name")}
        if platform.system().lower() == "windows":
            try:
                out = subprocess.check_output(["tasklist", "/FO", "CSV", "/NH"], text=True, encoding="utf-8", errors="ignore")
                names = set()
                for line in out.splitlines():
                    if not line.strip():
                        continue
                    name = line.split(",", 1)[0].strip().strip('"').lower()
                    if name:
                        names.add(name)
                return names
            except Exception:
                return set()
        return set()

    def _get_foreground_process(self) -> str | None:
        if platform.system().lower() != "windows":
            return None
        if psutil is None:
            return None
        try:
            user32 = ctypes.windll.user32
            hwnd = user32.GetForegroundWindow()
            if not hwnd:
                return None
            pid = ctypes.wintypes.DWORD()
            user32.GetWindowThreadProcessId(hwnd, ctypes.byref(pid))
            proc = psutil.Process(pid.value)
            return proc.name()
        except Exception:
            return None

    def _probe_hotkey_registration(self, hk: str) -> dict[str, Any]:
        if platform.system().lower() != "windows":
            return {"available": True, "reason": "non-windows-skip"}

        parts = hk.split("+")
        mods = 0
        key = parts[-1]

        mod_map = {"alt": 0x0001, "ctrl": 0x0002, "shift": 0x0004, "win": 0x0008}
        for p in parts[:-1]:
            mods |= mod_map.get(p, 0)

        vk = self._to_vk(key)
        if vk is None:
            return {"available": True, "reason": "unsupported-key"}

        user32 = ctypes.windll.user32
        hotkey_id = 0xBEEF
        ok = user32.RegisterHotKey(None, hotkey_id, mods, vk)
        if ok:
            user32.UnregisterHotKey(None, hotkey_id)
            return {"available": True}
        return {"available": False}

    @staticmethod
    def _to_vk(key: str) -> int | None:
        key = key.lower()
        if key.startswith("f") and key[1:].isdigit():
            idx = int(key[1:])
            if 1 <= idx <= 24:
                return 0x70 + idx - 1
        if len(key) == 1 and key.isalpha():
            return ord(key.upper())
        if len(key) == 1 and key.isdigit():
            return ord(key)
        named = {
            "tab": 0x09,
            "esc": 0x1B,
            "escape": 0x1B,
            "space": 0x20,
            "enter": 0x0D,
        }
        return named.get(key)
