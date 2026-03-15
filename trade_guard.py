#!/usr/bin/env python3
"""Trade guard: validates risk constraints before any order placement.

This script DOES NOT place orders. It prepares and validates a proposed order.
Use it as a gate before execution scripts.
"""

from __future__ import annotations

import json
from dataclasses import dataclass, asdict
from pathlib import Path

CONFIG_PATH = Path('/Users/openmac/.openclaw/workspace/trade_guard_config.json')


@dataclass
class GuardConfig:
    max_leverage: float = 5.0
    max_risk_pct_per_trade: float = 2.0
    max_notional_usdt: float = 25.0
    allow_symbols: tuple[str, ...] = ('DOGEUSDT', 'BTCUSDT', 'ETHUSDT')
    require_manual_confirmation: bool = True
    kill_switch: bool = False


def load_config() -> GuardConfig:
    if not CONFIG_PATH.exists():
        cfg = GuardConfig()
        CONFIG_PATH.write_text(json.dumps(asdict(cfg), ensure_ascii=False, indent=2), encoding='utf-8')
        return cfg
    raw = json.loads(CONFIG_PATH.read_text(encoding='utf-8'))
    return GuardConfig(
        max_leverage=float(raw.get('max_leverage', 5.0)),
        max_risk_pct_per_trade=float(raw.get('max_risk_pct_per_trade', 2.0)),
        max_notional_usdt=float(raw.get('max_notional_usdt', 25.0)),
        allow_symbols=tuple(raw.get('allow_symbols', ['DOGEUSDT', 'BTCUSDT', 'ETHUSDT'])),
        require_manual_confirmation=bool(raw.get('require_manual_confirmation', True)),
        kill_switch=bool(raw.get('kill_switch', False)),
    )


def validate_proposal(
    *,
    symbol: str,
    side: str,
    leverage: float,
    entry_price: float,
    stop_price: float,
    qty: float,
    account_equity_usdt: float,
    cfg: GuardConfig,
) -> tuple[bool, list[str], dict]:
    reasons: list[str] = []

    if cfg.kill_switch:
        reasons.append('kill_switch is ON')

    if symbol not in cfg.allow_symbols:
        reasons.append(f'symbol {symbol} not allowed')

    if side not in {'Buy', 'Sell'}:
        reasons.append('side must be Buy or Sell')

    if leverage <= 0 or leverage > cfg.max_leverage:
        reasons.append(f'leverage {leverage} exceeds max {cfg.max_leverage}')

    notional = entry_price * qty
    if notional > cfg.max_notional_usdt:
        reasons.append(f'notional {notional:.4f} > max_notional_usdt {cfg.max_notional_usdt:.4f}')

    per_unit_risk = abs(entry_price - stop_price)
    est_loss = per_unit_risk * qty
    risk_pct = (est_loss / account_equity_usdt * 100) if account_equity_usdt > 0 else 999.0

    if risk_pct > cfg.max_risk_pct_per_trade:
        reasons.append(
            f'risk_pct {risk_pct:.2f}% > max_risk_pct_per_trade {cfg.max_risk_pct_per_trade:.2f}%'
        )

    report = {
        'symbol': symbol,
        'side': side,
        'leverage': leverage,
        'entry_price': entry_price,
        'stop_price': stop_price,
        'qty': qty,
        'notional_usdt': round(notional, 6),
        'est_loss_usdt': round(est_loss, 6),
        'risk_pct': round(risk_pct, 4),
        'manual_confirmation_required': cfg.require_manual_confirmation,
    }

    return (len(reasons) == 0), reasons, report


def demo() -> None:
    cfg = load_config()
    ok, reasons, report = validate_proposal(
        symbol='DOGEUSDT',
        side='Buy',
        leverage=5,
        entry_price=0.096,
        stop_price=0.091,
        qty=100,
        account_equity_usdt=50,
        cfg=cfg,
    )

    print('=== TRADE GUARD DEMO ===')
    print(json.dumps(report, ensure_ascii=False, indent=2))
    print('allowed:', ok)
    if reasons:
        print('reasons:')
        for r in reasons:
            print('-', r)


if __name__ == '__main__':
    demo()
