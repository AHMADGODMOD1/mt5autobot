from __future__ import annotations
import asyncio
from datetime import datetime, timezone
from fastapi import FastAPI
from fastapi.responses import HTMLResponse
from .config import SYMBOLS, TIMEFRAMES, TRADING_MODE
from .mt5_gateway import connect, shutdown, account, positions
from .market_data import candles, snapshot
from .risk import validate
from .ai import decide
from .execution import execute

app = FastAPI(title="MT5 AI Autobot")
state = {"running":False,"started":False,"mode":TRADING_MODE,"last_signal":None,"last_error":None,"events":[]}

def event(kind, data):
    state["events"].insert(0,{"time":datetime.now(timezone.utc).isoformat(),"kind":kind,**data})
    del state["events"][100:]

@app.on_event("startup")
def startup():
    state["started"] = connect()

@app.on_event("shutdown")
def on_shutdown(): shutdown()

@app.get("/api/status")
def status():
    a=account(); ps=positions()
    return {"connected":state["started"],"running":state["running"],"mode":state["mode"],"balance":getattr(a,"balance",None),"equity":getattr(a,"equity",None),"margin":getattr(a,"margin",None),"free_margin":getattr(a,"margin_free",None),"positions":len(ps),"last_signal":state["last_signal"],"last_error":state["last_error"],"events":state["events"]}

@app.post("/api/control")
def control(body: dict):
    state["running"] = bool(body.get("running", state["running"]))
    return {"ok":True,"running":state["running"]}

@app.get("/api/chart/{symbol}")
def chart(symbol: str, tf: str="M5"):
    return {"symbol":symbol,"timeframe":tf,"candles":candles(symbol,tf,250),"tick":snapshot(symbol)}

async def worker():
    while True:
        if state["running"] and state["started"]:
            for symbol in SYMBOLS:
                try:
                    snap=snapshot(symbol); t=mt5_tick=snap
                    ask,bid=snap.get("ask"),snap.get("bid")
                    spread=abs(ask-bid) if ask is not None and bid is not None else 999999
                    a=account(); rd=validate(a,len(positions()),spread)
                    if not rd.allowed:
                        event("RISK_BLOCK",{"symbol":symbol,"reason":rd.reason}); continue
                    data={"symbol":symbol,"snapshot":snap,"D1":candles(symbol,"D1",60),"H4":candles(symbol,"H4",100),"H1":candles(symbol,"H1",120),"M15":candles(symbol,"M15",120),"M5":candles(symbol,"M5",120)}
                    sig=decide(data); state["last_signal"]={"symbol":symbol,**sig}
                    event("AI_SIGNAL",{"symbol":symbol,"signal":sig.get("signal"),"confidence":sig.get("confidence"),"logic":sig.get("logic")})
                    if sig.get("signal") in ("BUY","SELL") and float(sig.get("confidence",0)) >= 70:
                        result=execute(symbol,sig); event("EXECUTION",{"symbol":symbol,"result":result})
                except Exception as e:
                    state["last_error"]=str(e); event("ERROR",{"symbol":symbol,"error":str(e)})
                await asyncio.sleep(1)
        await asyncio.sleep(4)

@app.on_event("startup")
async def start_worker(): asyncio.create_task(worker())

@app.get("/", response_class=HTMLResponse)
def home():
    return open("app/static/index.html",encoding="utf-8").read()
