import requests

ASSETS = {
    "bitcoin": "BTC",
    "ethereum": "ETH",
    "dogecoin": "DOGE"
}

def get_data():
    try:
        ids = ",".join(ASSETS.keys())
        url = f"https://api.coingecko.com/api/v3/simple/price?ids={ids}&vs_currencies=usd&include_24hr_change=true"
        return requests.get(url, timeout=10).json()
    except:
        return {}

data = get_data()
for asset, symbol in ASSETS.items():
    change = data.get(asset, {}).get('usd_24h_change', 0)
    print(f"{symbol}: {change:.2f}%")
