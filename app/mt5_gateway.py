from __future__ import annotations
import MetaTrader5 as mt5

def connect():
    # No broker login/password/server is read by this app.
    # MetaTrader5.initialize() finds/starts the installed terminal and uses
    # the account already selected/saved inside MT5.
    return bool(mt5.initialize())

def shutdown(): mt5.shutdown()
def account(): return mt5.account_info()
def terminal(): return mt5.terminal_info()

def trading_permissions():
    a=account(); t=terminal()
    return {
        "terminal_connected": bool(getattr(t,"connected",False)),
        "algo_trading_enabled": bool(getattr(t,"trade_allowed",False)),
        "python_trade_api_enabled": not bool(getattr(t,"tradeapi_disabled",False)),
        "account_trade_allowed": bool(getattr(a,"trade_allowed",False)),
        "account_expert_allowed": bool(getattr(a,"trade_expert",False)),
        "login": getattr(a,"login",None),
        "server": getattr(a,"server",None),
    }

def can_algo_trade():
    p=trading_permissions()
    return all((p["terminal_connected"],p["algo_trading_enabled"],p["python_trade_api_enabled"],
               p["account_trade_allowed"],p["account_expert_allowed"]))

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
