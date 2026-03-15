# HEARTBEAT.md

## Trading monitor duties (main session)

On each heartbeat:
1. Read `/Users/openmac/.openclaw/workspace/.market_monitor_state.json`.
2. If `mode != ACTIVE` OR timestamp stale (>60s): restart watchdog stack and alert immediately.
3. Check Bybit snapshot via `./venv/bin/python /Users/openmac/.openclaw/workspace/bybit_monitor.py`.
4. If open positions > 0, send concise update to user:
   - ACTIVE status
   - open positions count + symbols
   - equity + total uPnL
   - notable action (if any: close/reduce/new entry)
5. If any TP/SL triggered or manual close executed, notify immediately with PnL.

Keep updates concise and operational.
