from __future__ import annotations

import json
from pathlib import Path
from typing import Any


class HotkeyRecordManager:
    def __init__(self, db_file: Path) -> None:
        self.db_file = db_file
        if not self.db_file.exists():
            self.db_file.write_text("[]", encoding="utf-8")

    def list_all(self) -> list[dict[str, Any]]:
        return json.loads(self.db_file.read_text(encoding="utf-8"))

    def save(self, record: dict[str, Any]) -> None:
        rows = self.list_all()
        rows.append(record)
        self.db_file.write_text(json.dumps(rows, ensure_ascii=False, indent=2), encoding="utf-8")

    def search(self, keyword: str) -> list[dict[str, Any]]:
        kw = keyword.lower().strip()
        if not kw:
            return self.list_all()
        out = []
        for row in self.list_all():
            text = json.dumps(row, ensure_ascii=False).lower()
            if kw in text:
                out.append(row)
        return out
