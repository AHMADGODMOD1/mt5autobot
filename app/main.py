from __future__ import annotations
import asyncio,MetaTrader5 as mt5
from fastapi import FastAPI,HTTPException
from fastapi.responses import HTMLResponse
from .config import SYMBOLS,TRADING_MODE,MIN_AI_CONFIDENCE,LOOP_SECONDS
from .mt5_gateway import connect,shutdown,account,positions,terminal,history
from .market_data import candles,snapshot
from .risk import validate
from .ai import decide
from .execution import execute
from .db import init_db,get_setting,set_setting,log_event,log_signal,log_execution,recent_events
app=FastAPI(title="MT5 AI Autobot")
state={"connected":False,"last_signal":None,"last_error":None}
def trading_enabled(): return get_setting("trading_enabled","0")=="1"
def event(kind,data,symbol=None): log_event(kind,data,symbol)
@app.on_event("startup")
def startup(): init_db(); state["connected"]=connect(); event("SYSTEM",{"connected":state["connected"]})
@app.on_event("shutdown")
def on_shutdown(): shutdown()
@app.get("/api/status")
def status():
    a,ps,t=account(),positions(),terminal()
    return {"connected":state["connected"],"trading_enabled":trading_enabled(),"mode":TRADING_MODE,"live_allowed":TRADING_MODE=="LIVE",
      "terminal":{"connected":getattr(t,"connected",False),"trade_allowed":getattr(t,"trade_allowed",False),"tradeapi_disabled":getattr(t,"tradeapi_disabled",False)},
      "account":{"login":getattr(a,"login",None),"name":getattr(a,"name",None),"server":getattr(a,"server",None),"currency":getattr(a,"currency",None),
      "balance":getattr(a,"balance",None),"equity":getattr(a,"equity",None),"margin":getattr(a,"margin",None),"free_margin":getattr(a,"margin_free",None),"profit":getattr(a,"profit",None)},
      "positions":len(ps),"position_items":[{"ticket":p.ticket,"symbol":p.symbol,"type":p.type,"volume":p.volume,"price_open":p.price_open,"sl":p.sl,"tp":p.tp,"profit":p.profit,"magic":getattr(p,"magic",None)} for p in ps],
      "last_signal":state["last_signal"],"last_error":state["last_error"],"events":recent_events(50)}
@app.post("/api/trading")
def trading(body:dict):
    enabled=bool(body.get("enabled",False))
    if enabled and not state["connected"]: raise HTTPException(503,"MT5 is not connected")
    set_setting("trading_enabled","1" if enabled else "0"); event("TRADING_ON" if enabled else "TRADING_OFF",{"enabled":enabled})
    return {"ok":True,"trading_enabled":enabled}
@app.post("/api/reconnect")
def reconnect():
    shutdown(); state["connected"]=connect(); event("RECONNECT",{"connected":state["connected"]}); return {"ok":state["connected"]}
@app.get("/api/chart/{symbol}")
def chart(symbol:str,tf:str="M5"): return {"symbol":symbol,"timeframe":tf,"candles":candles(symbol,tf,300),"tick":snapshot(symbol)}
@app.get("/api/history")
def trade_history(days:int=30):
    deals=history(max(1,min(days,90)))
    return [{"ticket":getattr(d,"ticket",None),"order":getattr(d,"order",None),"time":getattr(d,"time",None),
      "symbol":getattr(d,"symbol",None),"type":getattr(d,"type",None),"volume":getattr(d,"volume",None),
      "price":getattr(d,"price",None),"profit":getattr(d,"profit",None),"commission":getattr(d,"commission",None),
      "swap":getattr(d,"swap",None),"comment":getattr(d,"comment",None),"magic":getattr(d,"magic",None)} for d in deals]
async def worker():
    while True:
        if state["connected"] and trading_enabled():
            for symbol in SYMBOLS:
                try:
                    snap=snapshot(symbol); ask,bid=snap.get("ask"),snap.get("bid"); info=mt5.symbol_info(symbol)
                    point=getattr(info,"point",0.00001) if info else 0.00001
                    spread=abs(ask-bid)/point if ask is not None and bid is not None else 999999
                    rd=validate(account(),len(positions()),spread)
                    if not rd.allowed:
                        event("RISK_BLOCK",{"reason":rd.reason,"daily_loss_pct":rd.daily_loss_pct,"drawdown_pct":rd.drawdown_pct},symbol); continue
                    data={"symbol":symbol,"snapshot":snap,"D1":candles(symbol,"D1",60),"H4":candles(symbol,"H4",100),
                      "H1":candles(symbol,"H1",120),"M15":candles(symbol,"M15",120),"M5":candles(symbol,"M5",120)}
                    sig=decide(data); state["last_signal"]={"symbol":symbol,**sig}; log_signal(symbol,sig)
                    event("AI_SIGNAL",{"signal":sig.get("signal"),"confidence":sig.get("confidence"),"logic":sig.get("logic")},symbol)
                    if sig.get("signal") in ("BUY","SELL") and float(sig.get("confidence",0))>=MIN_AI_CONFIDENCE:
                        result=execute(symbol,sig); log_execution(symbol,result); event("EXECUTION",result,symbol)
                except Exception as e:
                    state["last_error"]=str(e); event("ERROR",{"error":str(e)},symbol)
                await asyncio.sleep(1)
        await asyncio.sleep(LOOP_SECONDS)
@app.on_event("startup")
async def start_worker(): asyncio.create_task(worker())
@app.get("/",response_class=HTMLResponse)
def home(): return open("app/static/index.html",encoding="utf-8").read()
