#!/usr/bin/env python3
from __future__ import annotations

import hashlib
import hmac
import json
import math
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict
from urllib.parse import urlencode

import requests

ENV_PATH = Path('/Users/openmac/.openclaw/workspace/.env.bybit')
LOG_PATH = Path('/Users/openmac/.openclaw/workspace/trades_log.jsonl')


def load_env(path: Path = ENV_PATH) -> Dict[str, str]:
    vals: Dict[str, str] = {}
    for line in path.read_text(encoding='utf-8').splitlines():
        s = line.strip()
        if not s or s.startswith('#') or '=' not in s:
            continue
        k, v = s.split('=', 1)
        vals[k.strip()] = v.strip()
    return vals


@dataclass
class BybitExec:
    api_key: str
    api_secret: str
    base_url: str
    recv_window: str = '5000'

    @classmethod
    def from_env(cls) -> 'BybitExec':
        vals = load_env()
        testnet = vals.get('BYBIT_TESTNET', 'false').lower() == 'true'
        base = 'https://api-testnet.bybit.com' if testnet else 'https://api.bybit.com'
        return cls(vals['BYBIT_API_KEY'], vals['BYBIT_API_SECRET'], base)

    def _sign(self, query: str, ts_ms: str) -> str:
        payload = ts_ms + self.api_key + self.recv_window + query
        return hmac.new(self.api_secret.encode(), payload.encode(), hashlib.sha256).hexdigest()

    def signed_get(self, path: str, params: Dict[str, Any]) -> Dict[str, Any]:
        q = urlencode(params)
        ts = str(int(time.time() * 1000))
        h = {
            'X-BAPI-API-KEY': self.api_key,
            'X-BAPI-TIMESTAMP': ts,
            'X-BAPI-RECV-WINDOW': self.recv_window,
            'X-BAPI-SIGN': self._sign(q, ts),
        }
        r = requests.get(f'{self.base_url}{path}?{q}', headers=h, timeout=20)
        r.raise_for_status()
        j = r.json()
        if j.get('retCode') != 0:
            raise RuntimeError(f"GET {path} failed: {j.get('retCode')} {j.get('retMsg')}")
        return j

    def signed_post(self, path: str, body: Dict[str, Any]) -> Dict[str, Any]:
        payload = json.dumps(body, separators=(',', ':'))
        ts = str(int(time.time() * 1000))
        sign_raw = ts + self.api_key + self.recv_window + payload
        sign = hmac.new(self.api_secret.encode(), sign_raw.encode(), hashlib.sha256).hexdigest()
        h = {
            'X-BAPI-API-KEY': self.api_key,
            'X-BAPI-TIMESTAMP': ts,
            'X-BAPI-RECV-WINDOW': self.recv_window,
            'X-BAPI-SIGN': sign,
            'Content-Type': 'application/json',
        }
        r = requests.post(f'{self.base_url}{path}', headers=h, data=payload, timeout=20)
        r.raise_for_status()
        j = r.json()
        if j.get('retCode') != 0:
            raise RuntimeError(f"POST {path} failed: {j.get('retCode')} {j.get('retMsg')}")
        return j

    def market_price(self, symbol: str) -> float:
        r = requests.get(
            f'{self.base_url}/v5/market/tickers',
            params={'category': 'linear', 'symbol': symbol},
            timeout=15,
        )
        r.raise_for_status()
        j = r.json()
        if j.get('retCode') != 0:
            raise RuntimeError(j.get('retMsg'))
        return float(j['result']['list'][0]['lastPrice'])

    def instrument(self, symbol: str) -> Dict[str, Any]:
        r = requests.get(
            f'{self.base_url}/v5/market/instruments-info',
            params={'category': 'linear', 'symbol': symbol},
            timeout=15,
        )
        r.raise_for_status()
        j = r.json()
        if j.get('retCode') != 0:
            raise RuntimeError(j.get('retMsg'))
        return j['result']['list'][0]


def floor_step(value: float, step: float) -> float:
    if step <= 0:
        return value
    return math.floor(value / step) * step


def place_micro_trade(symbol='DOGEUSDT', side='Buy', leverage=5, notional_usdt=10.0) -> Dict[str, Any]:
    c = BybitExec.from_env()

    px = c.market_price(symbol)
    inst = c.instrument(symbol)
    lot = inst.get('lotSizeFilter', {})
    qty_step = float(lot.get('qtyStep', '1'))
    min_qty = float(lot.get('minOrderQty', '1'))

    raw_qty = notional_usdt / px
    qty = floor_step(raw_qty, qty_step)
    if qty < min_qty:
        qty = min_qty

    final_notional = qty * px
    if final_notional > notional_usdt * 1.5:
        raise RuntimeError(
            f'Min order size too large for {symbol}: final_notional={final_notional:.4f} > target={notional_usdt:.4f}'
        )

    # set leverage (isolated)
    c.signed_post('/v5/position/set-leverage', {
        'category': 'linear',
        'symbol': symbol,
        'buyLeverage': str(leverage),
        'sellLeverage': str(leverage),
    })

    sl = px * (0.97 if side == 'Buy' else 1.03)
    tp = px * (1.04 if side == 'Buy' else 0.96)

    order = {
        'category': 'linear',
        'symbol': symbol,
        'side': side,
        'orderType': 'Market',
        'qty': str(qty),
        'timeInForce': 'IOC',
        'positionIdx': 0,
        'takeProfit': f'{tp:.6f}',
        'stopLoss': f'{sl:.6f}',
        'tpslMode': 'Full',
    }

    res = c.signed_post('/v5/order/create', order)
    out = {
        'ts': int(time.time()),
        'symbol': symbol,
        'side': side,
        'leverage': leverage,
        'market_price': px,
        'qty': qty,
        'notional_est': round(qty * px, 6),
        'tp': round(tp, 6),
        'sl': round(sl, 6),
        'orderId': (res.get('result') or {}).get('orderId'),
    }
    with LOG_PATH.open('a', encoding='utf-8') as f:
        f.write(json.dumps(out, ensure_ascii=False) + '\n')
    return out


if __name__ == '__main__':
    result = place_micro_trade()
    print(json.dumps(result, ensure_ascii=False, indent=2))
