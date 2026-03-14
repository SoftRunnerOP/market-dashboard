import requests
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.bar import Bar

console = Console()

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

def get_market_metrics():
    # Estimations for indexes that don't have open public free APIs
    return {
        "fng": 16, # Fear & Greed
        "dxy": 104.5, # Dollar Index
        "alt_season": 35 # Alt Season Index
    }

def display_dashboard():
    data = get_data()
    metrics = get_market_metrics()
    
    # Dashboard Structure
    table = Table(title="Market Sentiment Dashboard [PRO]", show_header=True, header_style="bold magenta")
    table.add_column("Asset", style="cyan")
    table.add_column("Price (USD)", style="white")
    table.add_column("24h Change (%)", style="bold")

    # Metrics Panel
    metrics_str = f"Fear & Greed: {metrics['fng']} | DXY: {metrics['dxy']} | Alt Season: {metrics['alt_season']}"
    console.print(Panel(metrics_str, title="Market Indexes", border_style="yellow"))

    for id, symbol in ASSETS.items():
        price = data.get(id, {}).get('usd', 0)
        change = data.get(id, {}).get('usd_24h_change', 0)
        color = "green" if change >= 0 else "red"
        
        # Format DOGE specifically to 4 decimals, others can be standard
        price_fmt = f"${price:.4f}" if symbol == "DOGE" else f"${price:,.2f}"
        
        table.add_row(
            symbol, 
            price_fmt, 
            f"[{color}]{change:+.2f}%[/]"
        )

    console.print(table)

if __name__ == "__main__":
    display_dashboard()
