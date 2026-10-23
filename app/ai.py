from __future__ import annotations
import json,re,requests
from .config import AI_PROVIDER,AI_BASE_URL,AI_API_KEY,AI_MODEL,AI_TIMEOUT_SECONDS,DEEPSEEK_API_KEY,DEEPSEEK_MODEL
SYSTEM="""You are the signal engine for a risk-controlled MT5 trading system.
Use only supplied market data. Never invent prices. Return JSON only:
{"signal":"BUY|SELL|WAIT","confidence":0-100,"entry":number|null,"stop_loss":number|null,"take_profit":number|null,"logic":"short explanation","risk_flags":[]}
Prefer WAIT when evidence is mixed. BUY/SELL requires a logical invalidation level. Do not provide position size."""
def _parse(raw):
    raw=raw.strip(); raw=re.sub(r"^\x60\x60\x60(?:json)?\s*|\s*\x60\x60\x60$","",raw,flags=re.I)
    try: obj=json.loads(raw)
    except json.JSONDecodeError:
        m=re.search(r"\{.*\}",raw,re.S)
        if not m: raise
        obj=json.loads(m.group(0))
    sig=str(obj.get("signal","WAIT")).upper()
    if sig not in {"BUY","SELL","WAIT"}: sig="WAIT"
    return {"signal":sig,"confidence":max(0,min(100,float(obj.get("confidence",0) or 0))),
            "entry":obj.get("entry"),"stop_loss":obj.get("stop_loss"),"take_profit":obj.get("take_profit"),
            "logic":str(obj.get("logic",""))[:1200],
            "risk_flags":obj.get("risk_flags",[]) if isinstance(obj.get("risk_flags",[]),list) else []}
def _call(base,key,model,payload):
    if not key: raise RuntimeError("LLM API key is not configured")
    body={"model":model,"temperature":0.1,"messages":[{"role":"system","content":SYSTEM},{"role":"user","content":json.dumps(payload,default=str)}]}
    r=requests.post(base+"/chat/completions",headers={"Authorization":"Bearer "+key,"Content-Type":"application/json"},json=body,timeout=AI_TIMEOUT_SECONDS)
    r.raise_for_status(); return _parse(r.json()["choices"][0]["message"]["content"])
def decide(payload):
    errors=[]
    if AI_PROVIDER in {"freellmapi","openai_compatible","omniroute"}:
        try:return _call(AI_BASE_URL,AI_API_KEY,AI_MODEL,payload)
        except Exception as e: errors.append(AI_PROVIDER+": "+str(e))
    if DEEPSEEK_API_KEY:
        try:return _call("https://api.deepseek.com",DEEPSEEK_API_KEY,DEEPSEEK_MODEL,payload)
        except Exception as e: errors.append("deepseek: "+str(e))
    return {"signal":"WAIT","confidence":0,"entry":None,"stop_loss":None,"take_profit":None,
            "logic":"No working LLM route: "+" | ".join(errors)[-1000:],"risk_flags":["AI_UNAVAILABLE"]}
