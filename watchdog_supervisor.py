#!/usr/bin/env python3
from __future__ import annotations

import subprocess
import time
from pathlib import Path

WORKDIR = Path('/Users/openmac/.openclaw/workspace')
WATCHDOG = WORKDIR / 'market_watchdog.py'
PY = WORKDIR / 'venv' / 'bin' / 'python'
PID_FILE = WORKDIR / '.market_watchdog.pid'


def is_running(pid: int) -> bool:
    try:
        Path(f'/proc/{pid}')
    except Exception:
        pass
    try:
        import os
        os.kill(pid, 0)
        return True
    except Exception:
        return False


def start_watchdog() -> int:
    p = subprocess.Popen([str(PY), str(WATCHDOG)], cwd=str(WORKDIR))
    PID_FILE.write_text(str(p.pid), encoding='utf-8')
    return p.pid


def get_pid() -> int | None:
    if not PID_FILE.exists():
        return None
    try:
        return int(PID_FILE.read_text(encoding='utf-8').strip())
    except Exception:
        return None


def main():
    while True:
        pid = get_pid()
        if pid is None or not is_running(pid):
            new_pid = start_watchdog()
            print(f'[supervisor] started watchdog pid={new_pid}', flush=True)
        time.sleep(15)


if __name__ == '__main__':
    main()
