#!/usr/bin/env python3
"""
PNZ RAM Monitor — macOS menu bar RAM usage tool
Replaces ram-watcher.sh with a live menu-bar indicator.

Color coding:
  🟢  < 60%   Normal
  🟡  60–79%  Moderate
  🔴  ≥ 80%   High — stays visible at a glance
"""

import rumps
import psutil

# ── Config ────────────────────────────────────────────────────────────────────
INTERVAL       = 5    # seconds between refreshes
WARN_THRESHOLD = 60   # % → yellow indicator
CRIT_THRESHOLD = 80   # % → red indicator
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
        self._sep_swap  = rumps.separator
        self._swap_item = rumps.MenuItem("Swap: –")
        self._sep_procs = rumps.separator
        self._hdr       = rumps.MenuItem("Top Processes by RAM")
        self._procs     = [rumps.MenuItem(f"  – [{i}]") for i in range(TOP_N)]
        self._sep_quit  = rumps.separator
        self._quit      = rumps.MenuItem(
                              "Quit RAM Monitor",
                              callback=rumps.quit_application
                          )

        self.menu = [
            self._summary,
            None,                   # separator
            self._swap_item,
            None,                   # separator
            self._hdr,
            *self._procs,
            None,                   # separator
            self._quit,
        ]

        # Run first tick immediately so title appears before first interval
        self._tick(None)

    # ── Refresh timer ─────────────────────────────────────────────────────────
    @rumps.timer(INTERVAL)
    def _tick(self, _):
        print(f"Tick: {self.title}") # Heartbeat for debugging
        vm   = psutil.virtual_memory()
        swap = psutil.swap_memory()

        pct   = vm.percent
        used  = vm.used  / (1024 ** 3)
        total = vm.total / (1024 ** 3)

        # ── Menu bar title (colour indicator + %) ─────────────
        # Removed color icons – using plain text title
        # No icon variable needed

        self.title = f"RAM {pct:.0f}%"

        # ── Summary line ───────────────────────────────────────
        self._summary.title = (
            f"RAM:  {used:.1f} GB / {total:.0f} GB  ({pct:.0f}%)"
        )

        # ── Swap line ──────────────────────────────────────────
        swap_used = swap.used / (1024 ** 3)
        swap_total = swap.total / (1024 ** 3) if swap.total else 0
        self._swap_item.title = (
            f"Swap: {swap_used:.1f} GB / {swap_total:.0f} GB"
            if swap.total else "Swap: none"
        )

        # ── Top-N processes ────────────────────────────────────
        try:
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
                mb = rss / (1024 ** 2)
                display = name[:30]
                self._procs[i].title = f"  {display:<30}  {mb:>6.0f} MB"

            # Clear unused slots
            for i in range(len(top), TOP_N):
                self._procs[i].title = "  –"

        except Exception:
            pass


if __name__ == "__main__":
    RAMMonitor().run()
