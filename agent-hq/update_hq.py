#!/usr/bin/env python3
import json
import subprocess
import datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parent
OUT = ROOT / "hq_data.json"
CONFIG_PATH = Path.home() / ".openclaw" / "openclaw.json"


def run_json(cmd):
    p = subprocess.run(cmd, capture_output=True, text=True)
    if p.returncode != 0:
        return {"error": p.stderr.strip() or p.stdout.strip(), "cmd": " ".join(cmd)}
    try:
        return json.loads(p.stdout)
    except Exception:
        return {"error": "invalid json", "raw": p.stdout[:500], "cmd": " ".join(cmd)}


def load_bots_from_config():
    bots = []
    if not CONFIG_PATH.exists():
        return bots
    cfg = json.loads(CONFIG_PATH.read_text())
    tg = ((cfg.get("channels") or {}).get("telegram") or {})
    accounts = tg.get("accounts") or {}
    for acc_id, acc in accounts.items():
        bots.append({
            "id": acc_id,
            "name": acc.get("name") or acc_id,
            "enabled": bool(acc.get("enabled", True)),
            "username": acc.get("username") or "",
            "role": (
                "trading" if "trader" in acc_id else (
                "design/marketing" if "graphic" in acc_id else (
                "development" if ("archiv" in acc_id or "archive" in acc_id or "dev" in acc_id) else "general")))
        })
    # Ensure one director (usually default account)
    if not any(b.get('id') == 'default' for b in bots):
        bots.append({
            "id": "default",
            "name": "Main",
            "enabled": bool(tg.get('enabled', True)),
            "username": "",
            "role": "director"
        })

    for b in bots:
        if b.get('id') == 'default':
            b['role'] = 'director'
    return bots


def classify_bot_status(bot_id, sessions):
    # default session key usually has no account id segment
    if bot_id == "default":
        matched = [s for s in sessions if ":telegram:direct:" in s.get("key", "")]
    else:
        matched = [s for s in sessions if f":telegram:{bot_id}:" in s.get("key", "")]

    if not matched:
        return "offline", None

    latest = max(matched, key=lambda x: x.get("updatedAt", 0))
    now_ms = int(datetime.datetime.now(datetime.timezone.utc).timestamp() * 1000)
    delta_min = (now_ms - int(latest.get("updatedAt", 0))) / 60000

    if delta_min <= 2:
        return "working", latest.get("key")
    if delta_min <= 30:
        return "idle", latest.get("key")
    return "offline", latest.get("key")


def main():
    status = run_json(["openclaw", "status", "--json"])
    sessions_raw = run_json(["openclaw", "sessions", "--all-agents", "--json"])

    if isinstance(sessions_raw, list):
        sessions = sessions_raw
    elif isinstance(sessions_raw, dict):
        sessions = sessions_raw.get("sessions") or sessions_raw.get("rows") or sessions_raw.get("data") or []
    else:
        sessions = []

    bots = load_bots_from_config()

    bot_cards = []
    for b in bots:
        st, key = classify_bot_status(b["id"], sessions)
        bot_cards.append({
            **b,
            "status": st,
            "activeKey": key
        })

    out = {
        "generatedAt": datetime.datetime.now().isoformat(timespec="seconds"),
        "summary": {
            "bots": len(bot_cards),
            "working": sum(1 for b in bot_cards if b["status"] == "working"),
            "idle": sum(1 for b in bot_cards if b["status"] == "idle"),
            "offline": sum(1 for b in bot_cards if b["status"] == "offline")
        },
        "bots": bot_cards,
        "status": status
    }

    OUT.write_text(json.dumps(out, ensure_ascii=False, indent=2))
    print(f"Wrote {OUT}")


if __name__ == "__main__":
    main()
