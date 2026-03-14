import market_dashboard
import sys

def check():
    data = market_dashboard.get_data()
    alerts = []
    
    # mapping ids back to names/symbols from market_dashboard
    for id, symbol in market_dashboard.ASSETS.items():
        change = data.get(id, {}).get('usd_24h_change', 0)
        if abs(change) > 5.0:
            alerts.append(f"{symbol}: {change:+.2f}%")
            
    if alerts:
        print("ALERT: The following assets have moved >5% in 24h:")
        for alert in alerts:
            print(f"- {alert}")
    else:
        print("OK")

if __name__ == "__main__":
    check()
