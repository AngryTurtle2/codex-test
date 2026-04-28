# Hotkey Guard MVP (Windows)

Hotkey Guard is a Windows-focused MVP that helps answer:

1. Which program is likely capturing a hotkey?
2. What that hotkey likely does?

It supports:
- **Mode A**: summon query by a global hotkey (default `Ctrl+Alt+K`, requires `keyboard` package and admin in some environments).
- **Mode B**: open main UI and query/search manually.

## Features in MVP

- Hotkey normalization (`f3`, `Ctrl + Alt + K`, etc.)
- Multi-strategy detector with confidence scoring:
  - System-reserved hotkey matching
  - Known app rule matching (includes Snipaste defaults like `F1`/`F3`)
  - Foreground process inference
  - Optional Win32 hotkey registration probe
- Hotkey record manager (store/search in JSON)
- Tkinter desktop UI for query + history

## Quick start (source)

```bash
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\\Scripts\\activate
pip install -r requirements.txt
python main.py
```

## Build EXE on Windows

### Option 1: PowerShell

```powershell
./scripts/build_exe.ps1
```

### Option 2: CMD

```bat
scripts\\build_exe.bat
```

Build output:

- `dist/HotkeyGuard.exe`

## GitHub Release automation

This repository includes `.github/workflows/release.yml`.

- Push a tag like `v0.1.0`
- GitHub Actions builds `HotkeyGuard.exe`
- EXE is zipped as `HotkeyGuard-windows-x64.zip`
- The zip is attached to the GitHub Release automatically

Example:

```bash
git tag v0.1.0
git push origin v0.1.0
```

## Notes

- This project targets **Windows** APIs for strongest detection.
- On non-Windows systems, Windows-specific probes degrade gracefully.
- Exact ownership of globally registered hotkeys is not exposed by public Win32 APIs; this tool gives evidence-based results with confidence.
