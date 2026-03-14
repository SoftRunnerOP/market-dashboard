import requests
import json
import time
import os

API_KEY = "CG-E1S3As15sNEzr2wPymEeUkLm"


def to_float(val, default=0.0):
    try:
        if isinstance(val, str) and val.endswith('%'):
            return float(val[:-1])
        return float(val)
    except Exception:
        return default


def compute_signal(fng_value: int, btc_change: float, dom_value: float) -> str:
    score = 50
    if fng_value <= 20:
        score += 20
    elif fng_value <= 35:
        score += 10
    elif fng_value >= 80:
        score -= 20
    elif fng_value >= 65:
        score -= 10

    if btc_change >= 2:
        score += 10
    elif btc_change <= -2:
        score -= 10

    if dom_value >= 58:
        score -= 10
    elif dom_value <= 45:
        score += 10

    if score >= 70:
        return "STRONG BUY"
    if score >= 55:
        return "BUY ZONE"
    if score <= 30:
        return "STRONG SELL"
    if score <= 45:
        return "SELL ZONE"
    return "NEUTRAL"


def fetch_data():
    data = {
        "fng": "N/A",
        "fng_change": 0.0,
        "dom": "N/A",
        "dom_change": 0.0,
        "dxy": "N/A",
        "dxy_change": 0.0,
        "alt_season": "N/A",
        "signal": "NEUTRAL",
        "prices": {},
        "updated": time.strftime("%H:%M:%S")
    }

    if os.path.exists("data.json"):
        try:
            with open("data.json", "r") as f:
                old = json.load(f)
            data.update(old)
        except Exception:
            pass

    old_dom = to_float(data.get("dom", 56.0), 56.0)

    # 1) Binance prices
    try:
        r = requests.get("https://api.binance.com/api/v3/ticker/24hr", timeout=10)
        tickers = r.json() if r.ok else []
        targets = ["BTCUSDT", "ETHUSDT", "DOGEUSDT"]
        for t in tickers:
            if t.get('symbol') in targets:
                sym = t['symbol'].replace('USDT', '')
                data['prices'][sym] = {
                    "price": float(t['lastPrice']),
                    "change": float(t['priceChangePercent'])
                }
    except Exception:
        pass

    # 2) CoinGecko global (dominance)
    try:
        headers = {'x-cg-demo-api-key': API_KEY}
        g = requests.get("https://api.coingecko.com/api/v3/global", headers=headers, timeout=10).json()
        dom_val = float(g['data']['market_cap_percentage']['btc'])
        data['dom'] = f"{dom_val:.1f}%"
        data['dom_change'] = dom_val - old_dom
        data['alt_season'] = "HIGH" if dom_val < 40 else "LOW"
    except Exception:
        pass

    # 3) F&G index + 24h delta (via last two points)
    try:
        f = requests.get("https://api.alternative.me/fng/?limit=2", timeout=10).json()
        now_v = float(f['data'][0]['value'])
        prev_v = float(f['data'][1]['value']) if len(f['data']) > 1 else now_v
        data['fng'] = str(int(now_v))
        data['fng_change'] = now_v - prev_v
    except Exception:
        pass

    # 4) DXY + daily delta from open/close (stooq)
    try:
        # Example: Symbol,Date,Time,Open,High,Low,Close,Volume
        dxy_csv = requests.get("https://stooq.com/q/l/?s=dx.f&f=sd2t2ohlcv&h&e=csv", timeout=10).text.strip().splitlines()
        if len(dxy_csv) >= 2:
            row = dxy_csv[1].split(',')
            open_p = float(row[3])
            close_p = float(row[6])
            data['dxy'] = f"{close_p:.3f}"
            data['dxy_change'] = ((close_p - open_p) / open_p) * 100 if open_p else 0.0
    except Exception:
        pass

    # 5) Composite signal
    btc_change = to_float(data.get('prices', {}).get('BTC', {}).get('change', 0.0), 0.0)
    fng_int = int(to_float(data.get('fng', 50), 50))
    dom_float = to_float(data.get('dom', 56.0), 56.0)
    data['signal'] = compute_signal(fng_int, btc_change, dom_float)

    data['updated'] = time.strftime("%H:%M:%S")
    with open("data.json", "w") as f:
        json.dump(data, f)


if __name__ == "__main__":
    fetch_data()
