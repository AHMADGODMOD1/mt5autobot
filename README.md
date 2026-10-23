# MT5 AI Autobot — Iron Mode

Windows-first MT5 AI trading system focused on fast analysis and capital protection.

## Architecture

MT5 (already logged in)
→ D1/H4/H1/M15/M5 market data
→ risk/spread filters
→ direct Google AI Studio / Gemini
→ independent validation
→ consensus gate
→ position sizing
→ MT5 order_check
→ MT5 order_send
→ dashboard + SQLite journal

The bot does not store broker login/password/server. MetaTrader 5 is logged in normally on Windows and the Python integration uses that active terminal session.

## AI

This final version uses Google AI Studio directly. FreeLLMAPI is not required.

Local .env:
```env
GOOGLE_API_KEY=YOUR_GOOGLE_AI_STUDIO_KEY
AI_FAST_MODEL=gemini-3.8-flash
AI_VALIDATOR_MODEL=gemini-3.8-flash
AI_MAX_CALLS_PER_CYCLE=2
```

The bot can run two independent analysis passes. A directional signal requires agreement. If Google is unavailable or the models disagree, the system returns WAIT and does not trade.

Free API quotas and model availability can change. No AI API provides a guaranteed profit rate or unlimited free tokens.

## Risk-first protections

Defaults are deliberately conservative:
- 0.25% risk per trade
- 2% daily loss guard
- 5% peak-equity drawdown guard
- maximum 3 open positions
- spread guard
- 120-second execution cooldown
- minimum 75 confidence
- AI disagreement = WAIT
- missing/invalid SL = no order
- MT5 Algo Trading/account expert permission required
- order_check before order_send

No system can guarantee profit or eliminate losses. The goal is to reject poor setups and cap damage when conditions go wrong.

## Windows setup

1. Install MetaTrader 5 and log into your account inside MT5.
2. Download/clone this repository.
3. Run setup.bat.
4. Open the generated .env.
5. Put your Google AI Studio API key only in GOOGLE_API_KEY.
6. Set SYMBOLS to the exact broker symbols.
7. Keep PAPER mode for testing.
8. Run start.bat.
9. Open http://127.0.0.1:8000.
10. Verify the account, permissions, market data and AI response.

## Live mode

Only after successful demo testing:
```env
TRADING_MODE=LIVE
ALLOW_LIVE_TRADING=true
```

Then enable TRADING ON in the dashboard. If MT5 Algo Trading, account expert trading or the risk engine blocks execution, no live order is sent.

## Security

Never commit .env or any API key. The repository contains only placeholders.

## Hosting

The source repository can be hosted on GitHub and the dashboard can be deployed separately. However, a cloud/Vercel server cannot directly operate the MT5 terminal installed on your Windows PC. The live execution worker therefore stays local beside MT5. This is intentional: broker credentials and the trading terminal remain on your machine.
