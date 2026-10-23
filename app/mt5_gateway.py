from __future__ import annotations
import MetaTrader5 as mt5

def connect():
    # No broker login/password/server is read by this app.
    # MetaTrader5.initialize() finds/starts the installed terminal and uses
    # the account already selected/saved inside MT5.
    return bool(mt5.initialize())

def shutdown():
    mt5.shutdown()

def account():
    return mt5.account_info()

def terminal():
    return mt5.terminal_info()

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

def resolve_symbol(symbol):
    """Return an exact broker symbol, auto-resolving common suffixes."""
    if mt5.symbol_info(symbol) is not None:
        mt5.symbol_select(symbol, True)
        return symbol

    base = symbol
    for suffix in ("m", ".m", "_m", "-m", "micro", "."):
        if base.lower().endswith(suffix.lower()):
            base = base[:-len(suffix)]
            break

    candidates = mt5.symbols_get()
    if not candidates:
        return None

    exact = []
    partial = []
    target = base.lower()
    for item in candidates:
        name = getattr(item, "name", "")
        low = name.lower()
        if low == target:
            exact.append(name)
        elif low.startswith(target) or target in low:
            partial.append(name)

    selected = (exact + partial)
    for name in selected:
        if mt5.symbol_select(name, True):
            return name
    return None

def tick(symbol):
    resolved = resolve_symbol(symbol)
    if not resolved:
        return None
    return mt5.symbol_info_tick(resolved)

def symbol_info(symbol):
    resolved = resolve_symbol(symbol) or symbol
    return mt5.symbol_info(resolved)

def rates(symbol,timeframe,count=300):
    resolved = resolve_symbol(symbol)
    if not resolved:
        return None
    return mt5.copy_rates_from_pos(resolved,timeframe,0,count)

def positions():
    return mt5.positions_get() or ()

def history(days=30):
    from datetime import datetime,timedelta,timezone
    end=datetime.now(timezone.utc); start=end-timedelta(days=days)
    return mt5.history_deals_get(start,end) or ()
