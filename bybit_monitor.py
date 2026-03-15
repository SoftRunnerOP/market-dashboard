#!/usr/bin/env python3
"""Bybit account monitor (read-only).

- Loads API credentials from .env.bybit
- Reads wallet balance, open positions, and open orders
- Prints concise risk snapshot
"""

from __future__ import annotations

import hashlib
import hmac
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict
from urllib.parse import urlencode

import requests


ENV_PATH = Path('/Users/openmac/.openclaw/workspace/.env.bybit')


@dataclass
class BybitClient:
    api_key: str
    api_secret: str
    base_url: str = 'https://api.bybit.com'
    recv_window: str = '5000'

    @classmethod
    def from_env_file(cls, path: Path = ENV_PATH) -> 'BybitClient':
        vals: Dict[str, str] = {}
        for line in path.read_text(encoding='utf-8').splitlines():
            s = line.strip()
            if not s or s.startswith('#') or '=' not in s:
                continue
            k, v = s.split('=', 1)
            vals[k.strip()] = v.strip()

        key = vals.get('BYBIT_API_KEY', '')
        secret = vals.get('BYBIT_API_SECRET', '')
        testnet = vals.get('BYBIT_TESTNET', 'false').lower() == 'true'
        base = 'https://api-testnet.bybit.com' if testnet else 'https://api.bybit.com'

        if not key or not secret:
            raise RuntimeError('BYBIT_API_KEY / BYBIT_API_SECRET not found in .env.bybit')

        return cls(api_key=key, api_secret=secret, base_url=base)

    def _sign(self, query: str, ts_ms: str) -> str:
        payload = ts_ms + self.api_key + self.recv_window + query
        return hmac.new(self.api_secret.encode(), payload.encode(), hashlib.sha256).hexdigest()

    def signed_get(self, path: str, params: Dict[str, Any]) -> Dict[str, Any]:
        query = urlencode(params)
        ts_ms = str(int(time.time() * 1000))
        sign = self._sign(query, ts_ms)
        headers = {
            'X-BAPI-API-KEY': self.api_key,
            'X-BAPI-TIMESTAMP': ts_ms,
            'X-BAPI-RECV-WINDOW': self.recv_window,
            'X-BAPI-SIGN': sign,
        }
        r = requests.get(f'{self.base_url}{path}?{query}', headers=headers, timeout=20)
        r.raise_for_status()
        data = r.json()
        if data.get('retCode') != 0:
            raise RuntimeError(f"Bybit API error: {data.get('retCode')} {data.get('retMsg')}")
        return data


def fmt_usd(v: Any) -> str:
    try:
        return f"${float(v):,.4f}"
    except Exception:
        return 'N/A'


def snapshot() -> None:
    c = BybitClient.from_env_file()

    wallet = c.signed_get('/v5/account/wallet-balance', {'accountType': 'UNIFIED'})
    positions = c.signed_get('/v5/position/list', {'category': 'linear', 'settleCoin': 'USDT'})
    orders = c.signed_get('/v5/order/realtime', {'category': 'linear', 'settleCoin': 'USDT'})

    coins = ((wallet.get('result') or {}).get('list') or [{}])[0].get('coin') or []
    usdt = next((x for x in coins if x.get('coin') == 'USDT'), None)

    pos_list = (positions.get('result') or {}).get('list') or []
    open_positions = [p for p in pos_list if float(p.get('size') or 0) != 0]

    ord_list = (orders.get('result') or {}).get('list') or []

    print('=== BYBIT MONITOR SNAPSHOT ===')
    print(f"Mode: {'TESTNET' if 'testnet' in c.base_url else 'MAINNET'}")
    if usdt:
        print(f"USDT walletBalance: {fmt_usd(usdt.get('walletBalance'))}")
        print(f"USDT equity:        {fmt_usd(usdt.get('equity'))}")
        print(f"USDT available:     {fmt_usd(usdt.get('availableToWithdraw') or usdt.get('availableToBorrow') or usdt.get('walletBalance'))}")
    else:
        print('USDT balance: N/A')

    print(f'Open positions: {len(open_positions)}')
    for p in open_positions[:10]:
        side = p.get('side', 'N/A')
        sym = p.get('symbol', 'N/A')
        size = p.get('size', '0')
        avg = p.get('avgPrice', 'N/A')
        upl = p.get('unrealisedPnl', 'N/A')
        lev = p.get('leverage', 'N/A')
        print(f' - {sym} {side} size={size} lev={lev} avg={avg} uPnL={upl}')

    print(f'Open orders: {len(ord_list)}')
    for o in ord_list[:10]:
        print(f" - {o.get('symbol')} {o.get('side')} {o.get('orderType')} qty={o.get('qty')} price={o.get('price')} status={o.get('orderStatus')}")


if __name__ == '__main__':
    snapshot()
