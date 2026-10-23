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

This version uses Google AI Studio directly. FreeLLMAPI is not required.

Local `.env` values:

    GOOGLE_API_KEY=YOUR_GOOGLE_AI_STUDIO_KEY
    AI_FAST_MODEL=gemini-3.8-flash
    AI_VALIDATOR_MODEL=gemini-3.8-flash
    AI_MAX_CALLS_PER_CYCLE=2

The bot runs independent analysis passes. A directional signal requires agreement. If Google is unavailable or the models disagree, the system returns WAIT and does not trade.

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
- broker minimum stop-distance validation
- MT5 Algo Trading/account expert permission required
- order_check must pass before order_send

No system can guarantee profit or eliminate losses. The goal is to reject poor setups and cap damage when conditions go wrong.

## Windows setup

1. Install MetaTrader 5 and log into your demo/live account inside MT5.
2. Download the latest repository ZIP.
3. Run `start.bat`.
4. The script uses the installed Python 3.12 and creates the virtual environment automatically.
5. On first run, `.env` is created.
6. Put your Google AI Studio API key only in `GOOGLE_API_KEY`.
7. Set `SYMBOLS` to the exact broker symbols shown in MT5 Market Watch.
8. Keep `TRADING_MODE=PAPER` for the first test.
9. Open `http://127.0.0.1:8000`.
10. Verify account, permissions, market data and AI response.

## Live mode

Do not switch live on until the bot has completed a demo/PAPER test.

When you are ready, change only these local `.env` values:

    TRADING_MODE=LIVE
    ALLOW_LIVE_TRADING=true

Restart `start.bat`, then enable `TRADING ON` in the dashboard.

The bot will still refuse an order when MT5 permissions, spread, daily loss, drawdown, position limit, cooldown, confidence, SL/TP validation, broker stop-distance or `order_check` fails.

## Security

Never commit `.env` or any API key. `.env.example` contains placeholders only. If an API key was ever committed to the public repository, revoke/rotate it in Google AI Studio and use the replacement only in your local `.env`.

## Hosting

The dashboard source can be hosted separately, but live MT5 execution stays local beside the MT5 terminal on Windows. A cloud/Vercel server cannot directly operate the MT5 terminal installed on your PC.
