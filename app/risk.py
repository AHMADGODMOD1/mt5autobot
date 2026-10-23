from __future__ import annotations
from dataclasses import dataclass
from datetime import datetime, timezone
from .config import MAX_DAILY_LOSS_PCT,MAX_DRAWDOWN_PCT,MAX_OPEN_POSITIONS,MAX_SPREAD_POINTS
from .db import get_setting,set_setting
@dataclass
class RiskDecision:
    allowed: bool
    reason: str
    daily_loss_pct: float=0.0
    drawdown_pct: float=0.0
def _state(account):
    day=datetime.now(timezone.utc).strftime("%Y-%m-%d")
    equity=float(account.equity or 0)
    if get_setting("risk_day")!=day:
        set_setting("risk_day",day); set_setting("day_start_equity",equity); set_setting("peak_equity",equity)
    peak=max(float(get_setting("peak_equity",equity) or equity),equity)
    set_setting("peak_equity",peak)
    start=float(get_setting("day_start_equity",equity) or equity)
    daily=max(0,(start-equity)/start*100) if start>0 else 100
    dd=max(0,(peak-equity)/peak*100) if peak>0 else 100
    return daily,dd
def validate(account,open_positions,spread_points):
    if account is None:return RiskDecision(False,"MT5 account unavailable")
    if open_positions>=MAX_OPEN_POSITIONS:return RiskDecision(False,"Maximum open positions reached")
    if spread_points>MAX_SPREAD_POINTS:return RiskDecision(False,f"Spread too high: {spread_points:.1f} points")
    if float(account.balance or 0)<=0:return RiskDecision(False,"Invalid account balance")
    daily,dd=_state(account)
    if daily>=MAX_DAILY_LOSS_PCT:return RiskDecision(False,f"Daily loss guard reached ({daily:.2f}%)",daily,dd)
    if dd>=MAX_DRAWDOWN_PCT:return RiskDecision(False,f"Peak drawdown guard reached ({dd:.2f}%)",daily,dd)
    return RiskDecision(True,"Risk checks passed",daily,dd)
