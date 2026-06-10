#!/usr/bin/env python3
"""
PNZ RAM Monitor — macOS menu bar RAM usage tool
Replaces ram-watcher.sh with a live menu-bar indicator.

Shows:  RAM <pct>%   in the menu bar, updates every INTERVAL seconds.
Dropdown: used/total GB, swap, top N processes by RSS.
"""

import rumps
import psutil
import socket
import sys
import os
from AppKit import NSStatusBar, NSVariableStatusItemLength

# ── Single-instance lock ──────────────────────────────────────────────────────
# Bind a Unix-domain socket to a fixed path. If another instance is already
# holding the socket, we exit immediately — preventing two NSStatusItems from
# fighting over the same menu-bar slot.
_LOCK_SOCK = socket.socket(socket.AF_UNIX, socket.SOCK_DGRAM)
_LOCK_PATH = "/tmp/com.pnz.ram-menubar.lock"
try:
    _LOCK_SOCK.bind(_LOCK_PATH)
except OSError:
    sys.exit(0)  # Another instance is already running — silently exit
# ─────────────────────────────────────────────────────────────────────────────

# ── Config ────────────────────────────────────────────────────────────────────
INTERVAL       = 5    # seconds between refreshes
WARN_THRESHOLD = 60   # % threshold for moderate usage
CRIT_THRESHOLD = 80   # % threshold for high usage
TOP_N          = 5    # processes shown in dropdown

IGNORE_NAMES = {
    "kernel_task", "WindowServer", "launchd", "loginwindow",
    "Dock", "Finder", "SystemUIServer", "com.apple.WebKit.WebContent",
    "com.apple.WebKit.Networking",
}
# ─────────────────────────────────────────────────────────────────────────────


class RAMMonitor(rumps.App):
    def __init__(self):
        super().__init__("RAM", quit_button=None)

        # ── Dropdown items ─────────────────────────────────────
        self._summary   = rumps.MenuItem("Calculating…")
        self._swap_item = rumps.MenuItem("Swap: –")
        self._hdr       = rumps.MenuItem("Top Processes by RAM")
        self._procs     = [rumps.MenuItem(f"  – [{i}]") for i in range(TOP_N)]
        self._quit      = rumps.MenuItem(
                              "Quit RAM Monitor",
                              callback=rumps.quit_application
                          )

        self.menu = [
            self._summary,
            None,
            self._swap_item,
            None,
            self._hdr,
            *self._procs,
            None,
            self._quit,
        ]

        # First tick immediately so the title is set before the first interval
        self._tick(None)

    # ── Refresh timer ─────────────────────────────────────────────────────────
    @rumps.timer(INTERVAL)
    def _tick(self, _):
        try:
            vm   = psutil.virtual_memory()
            swap = psutil.swap_memory()

            pct   = vm.percent
            used  = vm.used  / (1024 ** 3)
            total = vm.total / (1024 ** 3)

            # ── Menu bar title ─────────────────────────────────
            # ── Force visibility on Sonoma (menu bar overflow protection) ──
            # rumps creates NSStatusItem in _nsapp.nsstatusitem after run();
            # call setVisible_(True) every tick so macOS doesn't hide us.
            try:
                self._nsapp.nsstatusitem.setVisible_(True)
            except Exception:
                pass

            label = f"RAM {pct:.0f}%"
            self.title = label  # rumps setter


            # ── Summary line ───────────────────────────────────
            self._summary.title = (
                f"RAM:  {used:.1f} GB / {total:.0f} GB  ({pct:.0f}%)"
            )

            # ── Swap line ──────────────────────────────────────
            swap_used  = swap.used  / (1024 ** 3)
            swap_total = swap.total / (1024 ** 3) if swap.total else 0
            self._swap_item.title = (
                f"Swap: {swap_used:.1f} GB / {swap_total:.0f} GB"
                if swap.total else "Swap: none"
            )

            # ── Top-N processes ────────────────────────────────
            all_procs = []
            for p in psutil.process_iter(["name", "memory_info"]):
                try:
                    mi = p.info["memory_info"]
                    nm = p.info["name"] or "?"
                    if mi and nm not in IGNORE_NAMES:
                        all_procs.append((nm, mi.rss))
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    continue

            top = sorted(all_procs, key=lambda x: x[1], reverse=True)[:TOP_N]

            for i, (name, rss) in enumerate(top):
                mb      = rss / (1024 ** 2)
                display = name[:30]
                self._procs[i].title = f"  {display:<30}  {mb:>6.0f} MB"

            for i in range(len(top), TOP_N):
                self._procs[i].title = "  –"

        except Exception as e:
            self._log_err(f"_tick error: {e}")

    # ── Helpers ───────────────────────────────────────────────────────────────
    @staticmethod
    def _log_err(msg: str) -> None:
        import traceback, os
        log = os.path.expanduser("~/Library/Logs/ram-menubar-err.log")
        with open(log, "a") as f:
            f.write(msg + "\n")
            traceback.print_exc(file=f)


if __name__ == "__main__":
    RAMMonitor().run()
