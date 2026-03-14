import requests
import sys

ASSETS = {"bitcoin": "BTC", "ethereum": "ETH", "dogecoin": "DOGE"}
try:
    ids = ",".join(ASSETS.keys())
    url = f"https://api.coingecko.com/api/v3/simple/price?ids={ids}&vs_currencies=usd&include_24hr_change=true"
    data = requests.get(url, timeout=10).json()
    alerts = []
    for id, symbol in ASSETS.items():
        change = data.get(id, {}).get('usd_24h_change', 0)
        if abs(change) > 5.0:
            alerts.append(f"{symbol}: {change:.2f}%")
    
    if alerts:
        print("ALERT: " + ", ".join(alerts))
    else:
        print("OK")
except Exception as e:
    print(f"Error: {e}")
