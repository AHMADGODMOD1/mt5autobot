from __future__ import annotations
import MetaTrader5 as mt5
from .config import MAGIC_NUMBER, ALLOW_LIVE_TRADING, TRADING_MODE

def execute(symbol: str, signal: dict, volume: float = 0.01) -> dict:
    if signal.get("signal") not in ("BUY", "SELL"):
        return {"ok":False,"status":"NO_TRADE","reason":"Signal is WAIT"}
    if TRADING_MODE != "LIVE" or not ALLOW_LIVE_TRADING:
        return {"ok":True,"status":"PAPER","reason":"Live execution disabled","signal":signal}
    info = mt5.symbol_info(symbol); tick = mt5.symbol_info_tick(symbol)
    if info is None or tick is None:
        return {"ok":False,"status":"ERROR","reason":"Symbol/tick unavailable"}
    order_type = mt5.ORDER_TYPE_BUY if signal["signal"] == "BUY" else mt5.ORDER_TYPE_SELL
    price = tick.ask if order_type == mt5.ORDER_TYPE_BUY else tick.bid
    sl = signal.get("stop_loss"); tp = signal.get("take_profit")
    request = {"action":mt5.TRADE_ACTION_DEAL,"symbol":symbol,"volume":volume,"type":order_type,"price":price,"sl":sl or 0.0,"tp":tp or 0.0,"deviation":20,"magic":MAGIC_NUMBER,"comment":"MT5-AI-AUTOBOT","type_time":mt5.ORDER_TIME_GTC,"type_filling":mt5.ORDER_FILLING_IOC}
    result = mt5.order_send(request)
    return {"ok":bool(result and result.retcode == mt5.TRADE_RETCODE_DONE),"status":getattr(result,"retcode",None),"order":getattr(result,"order",None),"deal":getattr(result,"deal",None),"comment":getattr(result,"comment","")}
