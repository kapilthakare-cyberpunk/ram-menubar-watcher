# PNZ RAM Monitor

A lightweight macOS menu bar app that shows live RAM usage at a glance.

```
RAM 68%   ← appears in your menu bar, updates every 5 seconds
```

Click the title to see a dropdown with:
- Total / used memory and percentage
- Swap usage
- Top 5 processes by RAM consumption
- Quit button

---

## Requirements

| Dependency | Notes |
|------------|-------|
| macOS 12 Monterey or later | Tested on Ventura 13 / Sonoma 14 |
| Python 3.10+ | Installed via [Homebrew](https://brew.sh): `brew install python` |
| Homebrew Python **framework build** | Standard Homebrew `python@3.x` includes the required `Python.app` bundle |

> **Why Homebrew Python?** macOS menu bar apps require the `Python.app/Contents/MacOS/Python` GUI binary. The installer auto-detects and uses this binary so no manual configuration is needed.

---

## Install

```bash
git clone https://github.com/your-org/ram-menubar.git   # or copy the folder
cd ram-menubar
./install.sh
```

The installer will:
1. Create a project-local virtual environment (`.venv/`)
2. Install `rumps` and `psutil` into the venv
3. Detect the correct GUI-capable `Python.app` binary
4. Write a `LaunchAgent` plist to `~/Library/LaunchAgents/`
5. Bootstrap the agent into your GUI (Aqua) session immediately

After install the menu bar title `RAM <pct>%` appears within a few seconds.

---

## Uninstall

```bash
./uninstall.sh
```

This stops the LaunchAgent and removes the plist. The project folder (script, venv) is kept — delete it manually if desired.

---

## Configuration

Edit the constants at the top of `ram_menubar.py`:

```python
INTERVAL       = 5    # seconds between refreshes
WARN_THRESHOLD = 60   # % → yellow (🟡) indicator  [currently text-only]
CRIT_THRESHOLD = 80   # % → red   (🔴) indicator  [currently text-only]
TOP_N          = 5    # number of processes shown in dropdown
```

After changing the script, re-run `./install.sh` to reload the agent.

---

## Logs

| File | Purpose |
|------|---------|
| `~/Library/Logs/ram-menubar.log` | Standard output (heartbeat `Tick:` lines) |
| `~/Library/Logs/ram-menubar-err.log` | Errors and stack traces |

```bash
# Live log tail
tail -f ~/Library/Logs/ram-menubar.log
tail -f ~/Library/Logs/ram-menubar-err.log
```

---

## Troubleshooting

### Menu bar icon not visible after install

**1. Verify the agent is running**

```bash
launchctl print gui/$(id -u)/com.pnz.ram-menubar | grep -E "state|pid"
```
Expected: `state = running` and a valid `pid`.

**2. Check for errors**

```bash
cat ~/Library/Logs/ram-menubar-err.log
```

**3. Verify the correct binary is in use**

```bash
ps aux | grep ram_menubar.py | grep -v grep
```

The path shown must contain `Python.app/Contents/MacOS/Python`, **not** just `bin/python3.14`.

**4. Menu bar may be overcrowded**

Hold **⌘** and drag menu bar items left to make room, or use a utility like Bartender.

**5. Log out and back in**

Some macOS privacy grants only take full effect after a fresh login session.

### `ImportError: No module named rumps`

Re-run the installer — it will reinstall the venv dependencies:

```bash
./install.sh
```

### Agent crashes immediately

Check the error log (`ram-menubar-err.log`). Common causes:
- Python version mismatch — ensure Homebrew Python is installed: `brew install python`
- Broken venv — delete `.venv/` and re-run `./install.sh`

---

## How it works

```
install.sh
├── Creates .venv/ with rumps + psutil
├── Resolves Python.app GUI binary from the venv interpreter
│     .venv/bin/python3 → (symlink) → Homebrew bin/python3.14
│                                           ↓ realpath
│     .../Python.framework/Versions/3.14/Resources/Python.app/Contents/MacOS/Python
├── Writes ~/Library/LaunchAgents/com.pnz.ram-menubar.plist
│     • ProgramArguments: [Python.app binary, ram_menubar.py]
│     • LimitLoadToSessionType: Aqua   ← GUI session only
│     • PYTHONPATH: .venv/lib/python3.14/site-packages
└── launchctl bootstrap gui/<uid>      ← modern GUI-session bootstrap
```

`ram_menubar.py` uses [`rumps`](https://github.com/jaredks/rumps) (a thin PyObjC wrapper) to:
- Create an `NSStatusItem` (menu bar slot)
- Set its title string every `INTERVAL` seconds via a `@rumps.timer` callback
- Populate the dropdown menu with `psutil` memory data

---

## Project structure

```
ram-menubar/
├── ram_menubar.py   # App logic (rumps + psutil)
├── install.sh       # One-shot installer (venv, plist, launchctl bootstrap)
├── uninstall.sh     # Teardown (launchctl bootout, plist removal)
└── README.md        # This file
```
