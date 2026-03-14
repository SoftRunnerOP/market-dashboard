import requests

def check_assets():
    ids = "bitcoin,ethereum,dogecoin"
    url = f"https://api.coingecko.com/api/v3/simple/price?ids={ids}&vs_currencies=usd&include_24hr_change=true"
    data = requests.get(url, timeout=10).json()
    
    alerts = []
    for asset_id, info in data.items():
        change = info.get('usd_24h_change', 0)
        if abs(change) > 5:
            alerts.append(f"{asset_id.upper()}: {change:.2f}%")
            
    if alerts:
        print(f"ALERT: Significant market movement! {', '.join(alerts)}")
    else:
        print("OK: All asset movements < 5%. No alerts needed.")

if __name__ == "__main__":
    check_assets()
