import requests
import json

def fetch_and_save():
    try:
        # Fetch data
        global_res = requests.get("https://api.coingecko.com/api/v3/global", timeout=10).json()
        fng_res = requests.get("https://api.alternative.me/fng/", timeout=10).json()
        binance_res = requests.get("https://api.binance.com/api/v3/ticker/24hr", timeout=10).json()
        
        # Parse
        dom = global_res['data']['market_cap_percentage']['bitcoin']
        fng = fng_res['data'][0]['value']
        
        targets = ["BTCUSDT", "ETHUSDT", "DOGEUSDT"]
        prices = {}
        for t in binance_res:
            if t['symbol'] in targets:
                prices[t['symbol'].replace('USDT', '')] = {
                    "price": float(t['lastPrice']),
                    "change": float(t['priceChangePercent'])
                }
        
        # Save to data.json
        data = {
            "fng": fng,
            "dom": dom,
            "prices": prices,
            "updated": "Live"
        }
        with open("data.json", "w") as f:
            json.dump(data, f)
            
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    fetch_and_save()
