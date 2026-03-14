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

def get_fear_greed():
    try:
        data = requests.get("https://api.alternative.me/fng/", timeout=10).json()
        return int(data['data'][0]['value'])
    except:
        return 50

def display_dashboard():
    data = get_data()
    fng = get_fear_greed()
    
    # Fear & Greed Visual
    fg_color = "red" if fng < 40 else "green"
    fg_bar = Bar(100, 0, fng, color=fg_color)
    
    table = Table(title="Market Sentiment Dashboard [PRO]", show_header=True, header_style="bold magenta")
    table.add_column("Asset", style="cyan")
    table.add_column("Price", style="white")
    table.add_column("24h Change", style="bold")

    for id, symbol in ASSETS.items():
        price = data.get(id, {}).get('usd', 0)
        change = data.get(id, {}).get('usd_24h_change', 0)
        color = "green" if change >= 0 else "red"
        
        table.add_row(
            symbol, 
            f"${price:,.2f}", 
            f"[{color}]{change:+.2f}%[/]"
        )

    console.print(Panel(f"Fear & Greed Index: {fng}/100", title="Market Sentiment", border_style="yellow"))
    console.print(fg_bar)
    console.print(table)

if __name__ == "__main__":
    display_dashboard()
