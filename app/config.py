from __future__ import annotations
import os
from dotenv import load_dotenv

load_dotenv()

SYMBOLS=[s.strip() for s in os.getenv("SYMBOLS","EURUSDm,GBPUSDm,BTCUSDm,XAUUSDm").split(",") if s.strip()]
TIMEFRAMES=["D1","H4","H1","M15","M5"]
TRADING_MODE=os.getenv("TRADING_MODE","PAPER").upper()
ALLOW_LIVE_TRADING=os.getenv("ALLOW_LIVE_TRADING","false").lower()=="true"
RISK_PER_TRADE=float(os.getenv("RISK_PER_TRADE","0.25"))
MAX_DAILY_LOSS_PCT=float(os.getenv("MAX_DAILY_LOSS_PCT","2.0"))
MAX_DRAWDOWN_PCT=float(os.getenv("MAX_DRAWDOWN_PCT","5.0"))
MAX_OPEN_POSITIONS=int(os.getenv("MAX_OPEN_POSITIONS","3"))
MAX_SPREAD_POINTS=float(os.getenv("MAX_SPREAD_POINTS","80"))
MIN_AI_CONFIDENCE=float(os.getenv("MIN_AI_CONFIDENCE","75"))
LOOP_SECONDS=float(os.getenv("LOOP_SECONDS","5"))
ENTRY_COOLDOWN_SECONDS=int(os.getenv("ENTRY_COOLDOWN_SECONDS","120"))
MAGIC_NUMBER=int(os.getenv("MAGIC_NUMBER","260001"))

GOOGLE_API_KEY=os.getenv("GOOGLE_API_KEY","")
AI_FAST_MODEL=os.getenv("AI_FAST_MODEL","gemini-3.8-flash")
AI_DEEP_MODEL=os.getenv("AI_DEEP_MODEL","gemini-3.8-flash")
AI_VALIDATOR_MODEL=os.getenv("AI_VALIDATOR_MODEL","gemini-3.8-flash")
AI_TIMEOUT_SECONDS=float(os.getenv("AI_TIMEOUT_SECONDS","20"))
AI_MAX_CALLS_PER_CYCLE=int(os.getenv("AI_MAX_CALLS_PER_CYCLE","2"))
DB_PATH=os.getenv("DB_PATH","autobot.db")
