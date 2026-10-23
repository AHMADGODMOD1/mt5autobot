from __future__ import annotations
from datetime import datetime,timezone
import MetaTrader5 as mt5
from .config import MAGIC_NUMBER,ALLOW_LIVE_TRADING,TRADING_MODE,RISK_PER_TRADE,ENTRY_COOLDOWN_SECONDS
from .db import last_execution_time
from .mt5_gateway import can_algo_trade,trading_permissions

def _volume(info,symbol,side,price,sl,balance):
    if not sl or balance<=0: raise ValueError("Valid stop_loss and balance are required")
    typ=mt5.ORDER_TYPE_BUY if side=="BUY" else mt5.ORDER_TYPE_SELL
    loss=mt5.order_calc_profit(typ,symbol,1.0,price,float(sl))
    if loss is None or loss>=0: raise ValueError("Cannot calculate stop-loss risk")
    risk_money=balance*(RISK_PER_TRADE/100)
    step=float(info.volume_step or .01); vmin=float(info.volume_min or step); vmax=float(info.volume_max or 100)
    raw=risk_money/abs(float(loss))
    volume=max(vmin,min(vmax,(raw//step)*step))
    return round(volume,8),risk_money

def _fill(info):
    mode=getattr(info,"filling_mode",None)
    allowed={getattr(mt5,"ORDER_FILLING_FOK",0),getattr(mt5,"ORDER_FILLING_IOC",1),getattr(mt5,"ORDER_FILLING_RETURN",2)}
    return mode if mode in allowed else mt5.ORDER_FILLING_IOC

def execute(symbol,signal):
    side=signal.get("signal")
    if side not in ("BUY","SELL"): return {"ok":False,"status":"NO_TRADE","reason":"Signal is WAIT"}
    if TRADING_MODE!="LIVE" or not ALLOW_LIVE_TRADING:
        return {"ok":True,"status":"PAPER","reason":"Live execution disabled","signal":signal}
    if not can_algo_trade():
        return {"ok":False,"status":"ALGO_TRADING_BLOCKED","reason":"MT5 Algo Trading / account trading permission is OFF",
                "permissions":trading_permissions()}
    now=datetime.now(timezone.utc); last=last_execution_time(symbol)
    if last and (now-last).total_seconds()<ENTRY_COOLDOWN_SECONDS:
        return {"ok":False,"status":"COOLDOWN","reason":"Entry cooldown active"}
    info=mt5.symbol_info(symbol); tick=mt5.symbol_info_tick(symbol)
    if info is None or tick is None:return {"ok":False,"status":"ERROR","reason":"Symbol/tick unavailable"}
    mt5.symbol_select(symbol,True)
    price=tick.ask if side=="BUY" else tick.bid
    sl=float(signal.get("stop_loss") or 0); tp=float(signal.get("take_profit") or 0)
    if sl<=0:return {"ok":False,"status":"ERROR","reason":"Missing stop_loss"}
    if side=="BUY" and sl>=price:return {"ok":False,"status":"ERROR","reason":"BUY SL must be below entry"}
    if side=="SELL" and sl<=price:return {"ok":False,"status":"ERROR","reason":"SELL SL must be above entry"}
    if tp and ((side=="BUY" and tp<=price) or (side=="SELL" and tp>=price)):
        return {"ok":False,"status":"ERROR","reason":"Invalid take_profit"}
    positions=mt5.positions_get(symbol=symbol) or ()
    desired=mt5.POSITION_TYPE_BUY if side=="BUY" else mt5.POSITION_TYPE_SELL
    if any(getattr(p,"type",None)==desired and getattr(p,"magic",None)==MAGIC_NUMBER for p in positions):
        return {"ok":False,"status":"DUPLICATE","reason":"Existing same-direction bot position"}
    acc=mt5.account_info(); balance=float(acc.balance if acc else 0)
    try: volume,risk_money=_volume(info,symbol,side,price,sl,balance)
    except Exception as e:return {"ok":False,"status":"RISK_ERROR","reason":str(e)}
    digits=int(info.digits or 5)
    req={"action":mt5.TRADE_ACTION_DEAL,"symbol":symbol,"volume":volume,
         "type":mt5.ORDER_TYPE_BUY if side=="BUY" else mt5.ORDER_TYPE_SELL,
         "price":round(price,digits),"sl":round(sl,digits),"tp":round(tp,digits) if tp else 0.0,
         "deviation":20,"magic":MAGIC_NUMBER,"comment":"MT5-AI-AUTOBOT",
         "type_time":mt5.ORDER_TIME_GTC,"type_filling":_fill(info)}
    check=mt5.order_check(req)
    if check is None:return {"ok":False,"status":"ORDER_CHECK_ERROR","reason":str(mt5.last_error())}
    result=mt5.order_send(req)
    return {"ok":bool(result and result.retcode==mt5.TRADE_RETCODE_DONE),"status":getattr(result,"retcode",None),
            "order":getattr(result,"order",None),"deal":getattr(result,"deal",None),"comment":getattr(result,"comment",""),
            "volume":volume,"risk_money":risk_money}
