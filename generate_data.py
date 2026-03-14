import requests
import json
import time

def fetch_and_save():
    data = {"fng": 50, "dom": "N/A", "prices": {}, "signal": "Neutral", "score": 50}
    
    # Prices (Binance)
    try:
        r = requests.get("https://api.binance.com/api/v3/ticker/24hr", timeout=10).json()
        targets = ["BTCUSDT", "ETHUSDT", "DOGEUSDT"]
        for t in r:
            if t['symbol'] in targets:
                data['prices'][t['symbol'].replace('USDT', '')] = {
                    "price": float(t['lastPrice']),
                    "change": float(t['priceChangePercent'])
                }
    except: pass
    
    # Global & F&G
    try:
        g = requests.get("https://api.coingecko.com/api/v3/global", timeout=10).json()
        data['dom'] = f"{g['data']['market_cap_percentage']['btc']:.1f}%"
        f = requests.get("https://api.alternative.me/fng/", timeout=10).json()
        data['fng'] = int(f['data'][0]['value'])
        # Simple signal logic
        data['score'] = data['fng']
        if data['score'] < 30: data['signal'] = "STRONG BUY"
        elif data['score'] > 70: data['signal'] = "STRONG SELL"
        else: data['signal'] = "NEUTRAL"
    except: pass
        
    with open("data.json", "w") as f:
        json.dump(data, f)

if __name__ == "__main__":
    fetch_and_save()
