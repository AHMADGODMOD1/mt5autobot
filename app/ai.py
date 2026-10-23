from __future__ import annotations
import json,re,requests
from .config import GOOGLE_API_KEY,AI_FAST_MODEL,AI_VALIDATOR_MODEL,AI_TIMEOUT_SECONDS,AI_MAX_CALLS_PER_CYCLE

SYSTEM="""You are the decision engine inside a risk-controlled MT5 trading system.
Analyze ONLY supplied market data. Never invent prices or news.
Capital preservation comes before opportunity. WAIT is preferred when evidence is mixed.
BUY/SELL requires multi-timeframe agreement, a logical invalidation stop, acceptable RR and no obvious risk flag.
Return JSON only:
{"signal":"BUY|SELL|WAIT","confidence":0-100,"entry":number|null,"stop_loss":number|null,"take_profit":number|null,"rr":number|null,"logic":"short explanation","risk_flags":[],"setup":"short setup name"}
Do not provide position size. Do not promise profit."""

def _parse(raw):
    raw=raw.strip()
    raw=re.sub(r"^\x60\x60\x60(?:json)?\s*|\s*\x60\x60\x60$","",raw,flags=re.I)
    try: obj=json.loads(raw)
    except json.JSONDecodeError:
        m=re.search(r"\{.*\}",raw,re.S)
        if not m: raise
        obj=json.loads(m.group(0))
    sig=str(obj.get("signal","WAIT")).upper()
    if sig not in {"BUY","SELL","WAIT"}: sig="WAIT"
    try: conf=max(0,min(100,float(obj.get("confidence",0) or 0)))
    except: conf=0
    return {"signal":sig,"confidence":conf,"entry":obj.get("entry"),"stop_loss":obj.get("stop_loss"),
            "take_profit":obj.get("take_profit"),"rr":obj.get("rr"),"logic":str(obj.get("logic",""))[:1200],
            "risk_flags":obj.get("risk_flags",[]) if isinstance(obj.get("risk_flags",[]),list) else [],
            "setup":str(obj.get("setup",""))[:120]}

def _call(model,payload):
    url=f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent"
    body={"system_instruction":{"parts":[{"text":SYSTEM}]},
          "contents":[{"role":"user","parts":[{"text":json.dumps(payload,default=str)}]}],
          "generationConfig":{"temperature":0.05,"responseMimeType":"application/json"}}
    r=requests.post(url,params={"key":GOOGLE_API_KEY},json=body,timeout=AI_TIMEOUT_SECONDS)
    r.raise_for_status()
    data=r.json()
    return _parse(data["candidates"][0]["content"]["parts"][0]["text"])

def decide(payload):
    if not GOOGLE_API_KEY:
        return {"signal":"WAIT","confidence":0,"entry":None,"stop_loss":None,"take_profit":None,
                "rr":None,"logic":"Google AI Studio API key is not configured","risk_flags":["AI_UNAVAILABLE"],"setup":""}

    results=[]; errors=[]
    models=[AI_FAST_MODEL,AI_VALIDATOR_MODEL]
    models=models[:max(1,min(2,AI_MAX_CALLS_PER_CYCLE))]
    for model in models:
        try: results.append(_call(model,payload))
        except Exception as e: errors.append(f"{model}: {str(e)[-500:]}")

    if not results:
        return {"signal":"WAIT","confidence":0,"entry":None,"stop_loss":None,"take_profit":None,
                "rr":None,"logic":"Gemini unavailable; fail-closed to WAIT","risk_flags":["AI_UNAVAILABLE"]+errors,"setup":""}

    buys=[x for x in results if x["signal"]=="BUY"]
    sells=[x for x in results if x["signal"]=="SELL"]

    if len(buys)==len(results) or len(sells)==len(results):
        group=buys if buys else sells
        best=max(group,key=lambda x:x["confidence"])
        best["confidence"]=min(best["confidence"],sum(x["confidence"] for x in group)/len(group))
        best["risk_flags"]=list(dict.fromkeys(best["risk_flags"]+errors))
        return best

    return {"signal":"WAIT","confidence":min(max(x["confidence"] for x in results),69),
            "entry":None,"stop_loss":None,"take_profit":None,"rr":None,
            "logic":"AI models disagree; hard WAIT","risk_flags":["NO_CONSENSUS"]+errors,"setup":""}
