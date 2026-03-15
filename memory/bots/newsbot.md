# newsbot journal

Use this file for news channel sourcing, filtering rules, publishing cadence, and quality constraints.

Format:
- YYYY-MM-DD HH:MM — [tag] fact/decision/outcome

- 2026-03-15 17:10 — [sync] Newsbot archive initialized. Mandatory preflight: read this file before processing/publishing news.
- 2026-03-15 17:10 — [decision] Scope: bot handles news channel updates and publishes filtered market-relevant news summaries.
- 2026-03-15 17:12 — [sync] Telegram bot mapping confirmed by Mr X: `@Crypto_news_fst_bot` corresponds to local archive id `newsbot`.
- 2026-03-15 17:10 — [next] On each cycle: collect updates -> compare with archive state -> publish only non-duplicate/high-impact items -> append result here.
