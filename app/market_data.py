from __future__ import annotations
import pandas as pd
import MetaTrader5 as mt5
from .mt5_gateway import rates, tick

TF = {"M5": mt5.TIMEFRAME_M5, "M15": mt5.TIMEFRAME_M15, "H1": mt5.TIMEFRAME_H1, "H4": mt5.TIMEFRAME_H4, "D1": mt5.TIMEFRAME_D1}

def candles(symbol: str, tf: str, count: int = 200) -> list[dict]:
    raw = rates(symbol, TF[tf], count)
    if raw is None:
        return []
    df = pd.DataFrame(raw)
    if df.empty:
        return []
    df["time"] = pd.to_datetime(df["time"], unit="s", utc=True).astype(str)
    return df.to_dict("records")

def snapshot(symbol: str) -> dict:
    t = tick(symbol)
    return {"symbol": symbol, "bid": getattr(t, "bid", None), "ask": getattr(t, "ask", None), "last": getattr(t, "last", None), "time_msc": getattr(t, "time_msc", None)}
