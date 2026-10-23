from __future__ import annotations
import MetaTrader5 as mt5
from .config import MT5_PATH

def connect():
    return bool(mt5.initialize(path=MT5_PATH) if MT5_PATH else mt5.initialize())
def shutdown(): mt5.shutdown()
def account(): return mt5.account_info()
def terminal(): return mt5.terminal_info()
def tick(symbol):
    if not mt5.symbol_select(symbol,True): return None
    return mt5.symbol_info_tick(symbol)
def symbol_info(symbol): return mt5.symbol_info(symbol)
def rates(symbol,timeframe,count=300): return mt5.copy_rates_from_pos(symbol,timeframe,0,count)
def positions(): return mt5.positions_get() or ()
def history(days=30):
    from datetime import datetime,timedelta,timezone
    end=datetime.now(timezone.utc); start=end-timedelta(days=days)
    return mt5.history_deals_get(start,end) or ()
