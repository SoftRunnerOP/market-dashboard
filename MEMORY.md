# Dashboard Specs (Persistent Requirements)
- DOGE price must show 5 decimal places (e.g., 0.09550).
- BTC, ETH prices must show standard locale formatting.
- Metrics: Fear & Greed Index and BTC Dominance must be displayed prominently at the top.
- Visuals: Must use 24h % change with green/red color coding.
- Stability: Dashboard should never break if one API is slow; show "N/A" rather than crashing or hiding blocks.
- Automation: Python script updates data.json, site reads it.
