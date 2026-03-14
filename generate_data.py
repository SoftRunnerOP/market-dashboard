import requests
import json
import time

def fetch_and_save():
    # Defensive data structure
    data = {
        "fng": "N/A", 
        "dom": "N/A", 
        "prices": {"BTC": {"price": 0, "change": 0}, "ETH": {"price": 0, "change": 0}, "DOGE": {"price": 0, "change": 0}}, 
        "updated": time.strftime("%H:%M:%S")
    }
    
    # 1. Binance Prices
    try:
        r = requests.get("https://api.binance.com/api/v3/ticker/24hr", timeout=10).json()
        targets = {"BTCUSDT": "BTC", "ETHUSDT": "ETH", "DOGEUSDT": "DOGE"}
        for t in r:
            if t['symbol'] in targets:
                data['prices'][targets[t['symbol']]] = {
                    "price": float(t['lastPrice']),
                    "change": float(t['priceChangePercent'])
                }
    except Exception as e: print(f"Price error: {e}")
    
    # 2. Global Data (CoinGecko)
    try:
        r = requests.get("https://api.coingecko.com/api/v3/global", timeout=10).json()
        data['dom'] = str(round(r['data']['market_cap_percentage']['bitcoin'], 1)) + '%'
    except: pass
    
    # 3. F&G (Alternative)
    try:
        r = requests.get("https://api.alternative.me/fng/", timeout=10).json()
        data['fng'] = r['data'][0]['value']
    except: pass
        
    with open("data.json", "w") as f:
        json.dump(data, f)

if __name__ == "__main__":
    fetch_and_save()
