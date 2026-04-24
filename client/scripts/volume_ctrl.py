import curses
import subprocess

HOSTS = [
    "mreich@mreich-nano1",
    "mreich@mreich-nano2"
]

MIN_VOL = 0
MAX_VOL = 120
STEP = 6  # ~5% per step

def set_volume(vol):
    for host in HOSTS:
        subprocess.Popen(
            ["ssh", host, f"amixer -c 0 cset numid=6 {vol},{vol}"],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL
        )

def main(stdscr):
    curses.curs_set(0)
    stdscr.nodelay(False)

    vol = 48  # start at 40%

    while True:
        pct = int(vol / MAX_VOL * 100)
        bar = "█" * (pct // 5) + "░" * (20 - pct // 5)

        stdscr.clear()
        stdscr.addstr(0, 0, "Orin Volume Control")
        stdscr.addstr(1, 0, "──────────────────────────────")
        stdscr.addstr(2, 0, f"Volume: {pct}%  [{bar}]  ({vol}/120)")
        stdscr.addstr(4, 0, "↑/↓  adjust volume")
        stdscr.addstr(5, 0, "q    quit")
        stdscr.refresh()

        key = stdscr.getch()

        if key == curses.KEY_UP:
            vol = min(MAX_VOL, vol + STEP)
            set_volume(vol)
        elif key == curses.KEY_DOWN:
            vol = max(MIN_VOL, vol - STEP)
            set_volume(vol)
        elif key == ord('q'):
            break

curses.wrapper(main)