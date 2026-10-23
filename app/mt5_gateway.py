from __future__ import annotations
import MetaTrader5 as mt5
from .config import MT5_PATH

def connect() -> bool:
    return bool(mt5.initialize(path=MT5_PATH) if MT5_PATH else mt5.initialize())

def shutdown() -> None:
    mt5.shutdown()

def account():
    return mt5.account_info()

def tick(symbol: str):
    if not mt5.symbol_select(symbol, True):
        return None
    return mt5.symbol_info_tick(symbol)

def rates(symbol: str, timeframe, count: int = 300):
    return mt5.copy_rates_from_pos(symbol, timeframe, 0, count)

def positions():
    return mt5.positions_get() or ()
