from __future__ import annotations
from dataclasses import dataclass
from .config import MAX_DAILY_LOSS_PCT, MAX_DRAWDOWN_PCT, MAX_OPEN_POSITIONS, MAX_SPREAD_POINTS

@dataclass
class RiskDecision:
    allowed: bool
    reason: str

def validate(account, open_positions: int, spread_points: float) -> RiskDecision:
    if account is None:
        return RiskDecision(False, "MT5 account unavailable")
    if open_positions >= MAX_OPEN_POSITIONS:
        return RiskDecision(False, "Maximum open positions reached")
    if spread_points > MAX_SPREAD_POINTS:
        return RiskDecision(False, f"Spread too high: {spread_points:.1f} points")
    balance = float(account.balance or 0)
    equity = float(account.equity or 0)
    if balance > 0 and (balance - equity) / balance * 100 >= MAX_DAILY_LOSS_PCT:
        return RiskDecision(False, "Daily loss guard")
    if balance > 0 and (balance - equity) / balance * 100 >= MAX_DRAWDOWN_PCT:
        return RiskDecision(False, "Maximum drawdown guard")
    return RiskDecision(True, "Risk checks passed")
