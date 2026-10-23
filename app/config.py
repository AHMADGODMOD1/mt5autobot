from __future__ import annotations
import os
from dotenv import load_dotenv

load_dotenv()

SYMBOLS = [s.strip() for s in os.getenv("SYMBOLS", "EURUSDm,GBPUSDm,BTCUSDm,XAUUSDm").split(",") if s.strip()]
TIMEFRAMES = ["D1", "H4", "H1", "M15", "M5"]
TRADING_MODE = os.getenv("TRADING_MODE", "PAPER").upper()
ALLOW_LIVE_TRADING = os.getenv("ALLOW_LIVE_TRADING", "false").lower() == "true"
RISK_PER_TRADE = float(os.getenv("RISK_PER_TRADE", "0.25"))
MAX_DAILY_LOSS_PCT = float(os.getenv("MAX_DAILY_LOSS_PCT", "2.0"))
MAX_DRAWDOWN_PCT = float(os.getenv("MAX_DRAWDOWN_PCT", "5.0"))
MAX_OPEN_POSITIONS = int(os.getenv("MAX_OPEN_POSITIONS", "3"))
MAX_SPREAD_POINTS = float(os.getenv("MAX_SPREAD_POINTS", "80"))
MAGIC_NUMBER = int(os.getenv("MAGIC_NUMBER", "260001"))
MT5_PATH = os.getenv("MT5_PATH") or None
AI_PROVIDER = os.getenv("AI_PROVIDER", "deepseek")
DEEPSEEK_API_KEY = os.getenv("DEEPSEEK_API_KEY", "")
DEEPSEEK_MODEL = os.getenv("DEEPSEEK_MODEL", "deepseek-chat")
