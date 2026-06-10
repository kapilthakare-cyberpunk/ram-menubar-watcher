#!/Users/kapilthakare/scripts/ram-menubar/.venv/bin/python3
# <bitbar.title>RAM Monitor</bitbar.title>
# <bitbar.version>1.0</bitbar.version>
# <bitbar.author>PNZ</bitbar.author>
# <bitbar.author.github>kapilthakare</bitbar.author.github>
# <bitbar.desc>Shows live RAM usage and top processes</bitbar.desc>

import psutil
import os
import sys
import subprocess

# Configuration
WARN_THRESHOLD = 60
CRIT_THRESHOLD = 80
TOP_N = 5

IGNORE_NAMES = {
    "kernel_task", "WindowServer", "launchd", "loginwindow",
    "Dock", "Finder", "SystemUIServer", "com.apple.WebKit.WebContent",
    "com.apple.WebKit.Networking",
}

def confirm_and_kill(pid: int, name: str):
    # AppleScript dialog prompt
    script = f'''
    display dialog "Are you sure you want to terminate {name} (PID: {pid})?" \
    buttons {{"Cancel", "Terminate"}} \
    default button "Terminate" \
    with icon caution \
    with title "Confirm Force Quit"
    '''
    try:
        res = subprocess.run(["osascript", "-e", script], capture_output=True, text=True)
        if res.returncode == 0:
            try:
                os.kill(pid, 9)
            except PermissionError:
                alert = f'display alert "Permission Denied" message "You do not have permission to terminate {name}." as warning'
                subprocess.run(["osascript", "-e", alert])
            except ProcessLookupError:
                pass
    except Exception as e:
        alert = f'display alert "Error" message "{str(e)}" as warning'
        subprocess.run(["osascript", "-e", alert])

def main():
    try:
        vm = psutil.virtual_memory()
        swap = psutil.swap_memory()

        pct = vm.percent
        used = vm.used / (1024 ** 3)
        total = vm.total / (1024 ** 3)

        # Set title color based on threshold (using high-contrast system colors for Light and Dark modes)
        prefix = ""
        color_opt = ""
        if pct >= CRIT_THRESHOLD:
            prefix = "🔴 "
            color_opt = " | color=#FF3B30,#FF453A"
        elif pct >= WARN_THRESHOLD:
            prefix = "⚠️ "
            color_opt = " | color=#FF9500,#FF9F0A"

        print(f"{prefix}RAM {pct:.0f}%{color_opt}")
        print("---")
        print(f"RAM: {used:.1f} GB / {total:.0f} GB ({pct:.0f}%) | font=SFMono-Regular size=12")
        
        swap_used = swap.used / (1024 ** 3)
        swap_total = swap.total / (1024 ** 3) if swap.total else 0
        if swap.total:
            print(f"Swap: {swap_used:.1f} GB / {swap_total:.0f} GB | font=SFMono-Regular size=12")
        else:
            print("Swap: none | font=SFMono-Regular size=12")

        print("---")
        print("Top Processes by RAM | font=SFMono-Regular size=12")

        all_procs = []
        for p in psutil.process_iter(["name", "pid", "memory_info"]):
            try:
                mi = p.info["memory_info"]
                nm = p.info["name"] or "?"
                pid = p.info["pid"]
                if mi and nm not in IGNORE_NAMES:
                    all_procs.append((nm, mi.rss, pid))
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                continue

        top = sorted(all_procs, key=lambda x: x[1], reverse=True)[:TOP_N]

        script_path = os.path.realpath(__file__)
        for name, rss, pid in top:
            mb = rss / (1024 ** 2)
            # Remove pipes and quotes to ensure safe command parsing in SwiftBar
            clean_name = name.replace('|', ' ').replace('"', '').replace("'", "").strip()
            display_name = clean_name[:20]
            # Print with monospaced font alignment and confirmation action
            print(f"  {display_name:<20} {mb:>6.0f} MB | font=SFMono-Regular size=12 bash={script_path} param0=kill param1={pid} param2='{clean_name}' terminal=false refresh=true")

        for _ in range(len(top), TOP_N):
            print("  – | font=SFMono-Regular size=12")

    except Exception as e:
        print("RAM ?%")
        print("---")
        print(f"Error: {e}")

if __name__ == "__main__":
    with open("/tmp/ram_menubar_kill.log", "a") as f:
        f.write(f"ARGS: {sys.argv}\n")
    if len(sys.argv) > 1 and sys.argv[1] == "kill":
        confirm_and_kill(int(sys.argv[2]), sys.argv[3])
    else:
        main()
