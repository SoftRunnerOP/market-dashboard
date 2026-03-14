import urllib.request
import json

ASSETS = {
    "bitcoin": "BTC",
    "ethereum": "ETH",
    "dogecoin": "DOGE"
}

def get_data():
    try:
        ids = ",".join(ASSETS.keys())
        url = f"https://api.coingecko.com/api/v3/simple/price?ids={ids}&vs_currencies=usd&include_24hr_change=true"
        with urllib.request.urlopen(url, timeout=10) as response:
            return json.loads(response.read().decode())
    except Exception as e:
        print(f"Error: {e}")
        return {}

data = get_data()
alerts = []

for asset_id, symbol in ASSETS.items():
    change = data.get(asset_id, {}).get('usd_24h_change', 0)
    if abs(change) > 5:
        alerts.append(f"{symbol}: {change:+.2f}%")

print(f"DEBUG: {data}")
if alerts:
    print("ALERT: " + ", ".join(alerts))
else:
    print("OK")
