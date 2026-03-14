#!/usr/bin/env python3
import json
import subprocess
import datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parent
OUT = ROOT / "hq_data.json"


def run_json(cmd):
    p = subprocess.run(cmd, capture_output=True, text=True)
    if p.returncode != 0:
        return {"error": p.stderr.strip() or p.stdout.strip(), "cmd": " ".join(cmd)}
    try:
        return json.loads(p.stdout)
    except Exception:
        return {"error": "invalid json", "raw": p.stdout[:500], "cmd": " ".join(cmd)}


def classify_session(s):
    updated = s.get("updatedAt")
    if not updated:
        return "unknown"
    # updatedAt is ms epoch
    now_ms = int(datetime.datetime.now(datetime.timezone.utc).timestamp() * 1000)
    delta_min = (now_ms - int(updated)) / 60000
    if delta_min <= 2:
        return "working"
    if delta_min <= 20:
        return "idle"
    return "offline"


def main():
    status = run_json(["openclaw", "status", "--json"])
    sessions = run_json(["openclaw", "sessions", "--all-agents", "--json"])

    # Gateway cron jobs via CLI tool output unavailable as json in openclaw, use internal cron tool not available here.
    # Keep minimal robust summary from sessions.
    cards = []
    if isinstance(sessions, dict):
        # openclaw sessions --json may return array or dict depending version
        rows = sessions.get("sessions") if "sessions" in sessions else sessions.get("rows")
        if rows is None and isinstance(sessions.get("data"), list):
            rows = sessions.get("data")
        if rows is None and isinstance(sessions, list):
            rows = sessions
    elif isinstance(sessions, list):
        rows = sessions
    else:
        rows = []

    for s in rows or []:
        cards.append({
            "key": s.get("key", "unknown"),
            "name": s.get("displayName") or s.get("key", "unknown"),
            "model": s.get("model", "-"),
            "tokens": s.get("totalTokens", 0),
            "status": classify_session(s),
            "updatedAt": s.get("updatedAt"),
            "kind": s.get("kind", "-")
        })

    out = {
        "generatedAt": datetime.datetime.now().isoformat(timespec="seconds"),
        "status": status,
        "sessions": cards,
        "summary": {
            "total": len(cards),
            "working": sum(1 for c in cards if c["status"] == "working"),
            "idle": sum(1 for c in cards if c["status"] == "idle"),
            "offline": sum(1 for c in cards if c["status"] == "offline")
        }
    }

    OUT.write_text(json.dumps(out, ensure_ascii=False, indent=2))
    print(f"Wrote {OUT}")


if __name__ == "__main__":
    main()
