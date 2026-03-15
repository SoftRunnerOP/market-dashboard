# main bot journal

Use this file for concise durable facts, decisions, and constraints from the main chat.

Format:
- YYYY-MM-DD HH:MM — fact/decision/outcome
- 2026-03-15 12:30 — Cron stack active: DataJsonUpdater runs minutely (generate_data.py -> update_hq.py -> commit/push only on staged changes; silent on success).
- 2026-03-15 12:30 — MarketMonitorAlerts rule confirmed: alert only if DOGE |24h| >= 5% OR signal/risk_level changed; otherwise exact output NO_REPLY.
- 2026-03-15 12:30 — Latest updater run committed and pushed market-dashboard commit 6cfea32 ("Auto Update").
- 2026-03-15 13:00 — DataJsonUpdater kept minutely cadence; latest observed market-dashboard commit advanced to 36bc1fe (Auto Update), with rapid intermediate commits 6ddbc96..6617a0c.
- 2026-03-15 13:21 — Mr X initialized "archivist" role for main; durable mode set: log key decisions/facts, keep dated concise journals, provide fast summaries/search on demand.
- 2026-03-15 13:21 — Explicit promise in archivist initialization: no file deletions without owner approval.
- 2026-03-15 14:00 — DataJsonUpdater 14:00 run committed and pushed market-dashboard update b14cc76 (Auto Update), advancing HEAD from 0de7c39.
- 2026-03-15 14:00 — Main dialog added role shift: initialize as "крипто ньюс бот" for Mr X with high-impact filtering and explicit no-financial-decisions-without-confirmation constraint.
- 2026-03-15 14:30 — DataJsonUpdater cron completed successfully; market-dashboard updated with commit b088234 (Auto Update), remote moved 67d7ac6 → b088234.
- 2026-03-15 14:30 — MarketMonitorAlerts evaluated fresh data and emitted NO_REPLY (DOGE 24h 1.253%, signal STRONG BUY, risk LOW unchanged).
- 2026-03-15 14:40 — [sync] Archive protocol activated: main must read `memory/bots/main.md` before actions and append post-action log lines with tags.
