from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path
import tkinter as tk
from tkinter import ttk, messagebox

from .detector import HotkeyDetector
from .manager import HotkeyRecordManager
from .global_summon import GlobalSummon

BASE_DIR = Path(__file__).resolve().parents[2]
RULES_FILE = BASE_DIR / "data" / "known_hotkeys.json"
DB_FILE = BASE_DIR / "data" / "records.json"


class HotkeyGuardApp:
    def __init__(self) -> None:
        self.detector = HotkeyDetector(RULES_FILE)
        self.manager = HotkeyRecordManager(DB_FILE)

        self.root = tk.Tk()
        self.root.title("Hotkey Guard MVP")
        self.root.geometry("880x560")
        self.summon = GlobalSummon(self.root)

        self.hotkey_var = tk.StringVar(value="F3")
        self.search_var = tk.StringVar(value="")

        top = ttk.Frame(self.root, padding=12)
        top.pack(fill=tk.X)

        ttk.Label(top, text="查询快捷键:").pack(side=tk.LEFT)
        ttk.Entry(top, textvariable=self.hotkey_var, width=24).pack(side=tk.LEFT, padx=8)
        ttk.Button(top, text="检测", command=self.detect_hotkey).pack(side=tk.LEFT)
        ttk.Button(top, text="启用全局唤起(Ctrl+Alt+K)", command=self.enable_summon).pack(side=tk.LEFT, padx=8)

        ttk.Separator(self.root).pack(fill=tk.X, pady=8)

        self.result = tk.Text(self.root, height=12, wrap="word")
        self.result.pack(fill=tk.X, padx=12)

        mid = ttk.Frame(self.root, padding=12)
        mid.pack(fill=tk.X)

        ttk.Label(mid, text="搜索历史:").pack(side=tk.LEFT)
        ttk.Entry(mid, textvariable=self.search_var, width=24).pack(side=tk.LEFT, padx=8)
        ttk.Button(mid, text="搜索", command=self.search).pack(side=tk.LEFT)
        ttk.Button(mid, text="刷新全部", command=self.refresh_records).pack(side=tk.LEFT, padx=8)

        self.table = ttk.Treeview(self.root, columns=("time", "hotkey", "owner", "confidence"), show="headings")
        self.table.heading("time", text="时间")
        self.table.heading("hotkey", text="快捷键")
        self.table.heading("owner", text="捕获者")
        self.table.heading("confidence", text="置信度")
        self.table.pack(fill=tk.BOTH, expand=True, padx=12, pady=6)

        self.refresh_records()

    def enable_summon(self) -> None:
        self.summon.start()

    def detect_hotkey(self) -> None:
        hotkey = self.hotkey_var.get().strip()
        if not hotkey:
            messagebox.showwarning("提示", "请输入快捷键")
            return

        try:
            detected = self.detector.detect(hotkey)
        except ValueError as exc:
            messagebox.showerror("格式错误", str(exc))
            return
        except Exception as exc:
            messagebox.showerror("检测失败", str(exc))
            return

        payload = detected.to_dict()
        payload["time"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.manager.save(payload)

        self.result.delete("1.0", tk.END)
        self.result.insert(
            tk.END,
            json.dumps(payload, ensure_ascii=False, indent=2),
        )
        self.refresh_records()

    def refresh_records(self) -> None:
        for item in self.table.get_children():
            self.table.delete(item)

        for row in reversed(self.manager.list_all()):
            self.table.insert(
                "",
                tk.END,
                values=(row.get("time"), row.get("hotkey"), row.get("owner"), row.get("confidence")),
            )

    def search(self) -> None:
        rows = self.manager.search(self.search_var.get())
        for item in self.table.get_children():
            self.table.delete(item)
        for row in reversed(rows):
            self.table.insert(
                "",
                tk.END,
                values=(row.get("time"), row.get("hotkey"), row.get("owner"), row.get("confidence")),
            )

    def run(self) -> None:
        self.root.mainloop()


def main() -> None:
    app = HotkeyGuardApp()
    app.run()


if __name__ == "__main__":
    main()
