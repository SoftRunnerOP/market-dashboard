import requests
import json
import time
import os

API_KEY = "CG-E1S3As15sNEzr2wPymEeUkLm"


def parse_percent(value, default=0.0):
    try:
        if isinstance(value, str) and value.endswith('%'):
            return float(value[:-1])
        return float(value)
    except Exception:
        return default


def compute_signal(fng_value: int, btc_change: float, dom_value: float) -> str:
    # Simple, transparent scoring
    score = 50
    # Fear/greed (contrarian)
    if fng_value <= 20:
        score += 20
    elif fng_value <= 35:
        score += 10
    elif fng_value >= 80:
        score -= 20
    elif fng_value >= 65:
        score -= 10

    # BTC momentum
    if btc_change >= 2:
        score += 10
    elif btc_change <= -2:
        score -= 10

    # Dominance pressure on alts
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
    # Preserve previous values on partial API failures
    data = {
        "fng": "N/A",
        "dom": "N/A",
        "dxy": "104.5",
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

    # 1) Binance prices (reliable)
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

    # 2) CoinGecko global + F&G
    try:
        headers = {'x-cg-demo-api-key': API_KEY}
        g = requests.get("https://api.coingecko.com/api/v3/global", headers=headers, timeout=10).json()
        dom_val = float(g['data']['market_cap_percentage']['btc'])
        data['dom'] = f"{dom_val:.1f}%"
        data['alt_season'] = "HIGH" if dom_val < 40 else "LOW"
    except Exception:
        pass

    try:
        f = requests.get("https://api.alternative.me/fng/", timeout=10).json()
        data['fng'] = str(f['data'][0]['value'])
    except Exception:
        pass

    # 3) Compute signal from available values
    btc_change = parse_percent(data.get('prices', {}).get('BTC', {}).get('change', 0.0), 0.0)
    fng_int = int(parse_percent(data.get('fng', 50), 50))
    dom_float = parse_percent(data.get('dom', 56.0), 56.0)
    data['signal'] = compute_signal(fng_int, btc_change, dom_float)

    data['updated'] = time.strftime("%H:%M:%S")
    with open("data.json", "w") as f:
        json.dump(data, f)


if __name__ == "__main__":
    fetch_data()
