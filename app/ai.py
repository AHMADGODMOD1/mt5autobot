from __future__ import annotations
import json
import requests
from .config import DEEPSEEK_API_KEY, DEEPSEEK_MODEL

SYSTEM = '''You are a trading analysis engine. Return JSON only. Never invent prices. Analyze supplied market data and produce a conservative candidate signal. Schema: {"signal":"BUY|SELL|WAIT","confidence":0-100,"entry":number|null,"stop_loss":number|null,"take_profit":number|null,"logic":"short explanation","risk_flags":[]}. WAIT is preferred when evidence is weak.'''

def decide(payload: dict) -> dict:
    if not DEEPSEEK_API_KEY:
        return {"signal":"WAIT","confidence":0,"entry":None,"stop_loss":None,"take_profit":None,"logic":"AI key not configured","risk_flags":["AI_NOT_CONFIGURED"]}
    body = {"model": DEEPSEEK_MODEL, "temperature": 0.1, "messages":[{"role":"system","content":SYSTEM},{"role":"user","content":json.dumps(payload, default=str)}]}
    r = requests.post("https://api.deepseek.com/chat/completions", headers={"Authorization":f"Bearer {DEEPSEEK_API_KEY}","Content-Type":"application/json"}, json=body, timeout=30)
    r.raise_for_status()
    text = r.json()["choices"][0]["message"]["content"]
    return json.loads(text)
