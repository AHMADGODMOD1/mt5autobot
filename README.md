# MT5 AI Autobot

Local-first MT5 AI execution system with persistent Trading ON/OFF, multi-timeframe analysis, OpenAI-compatible LLM routing, risk vetoes, dynamic position sizing, execution checks, live account monitoring and trade history.

## Included

MT5 -> D1/H4/H1/M15/M5 -> LLM gateway -> JSON signal -> risk engine -> broker-aware position sizing -> MT5 execution -> dashboard/journal.

Safety controls:
- PAPER mode by default
- persistent Trading ON/OFF
- daily loss guard
- peak-equity drawdown guard
- max open positions
- spread filter
- AI confidence threshold
- entry cooldown
- duplicate same-direction protection
- MT5 order_check before order_send
- broker volume step/min/max
- automatic position sizing from stop-loss risk
- LLM failure fallback to WAIT

## LLM routing

The bot accepts any OpenAI-compatible /v1/chat/completions gateway.

FreeLLMAPI:
1. Install its Windows desktop release.
2. Start it and add your provider keys.
3. Copy the unified API key.
4. Use:
   AI_BASE_URL=http://localhost:3001/v1
   AI_MODEL=auto
   AI_API_KEY=your-unified-key

FreeLLMAPI documents a local /v1 interface, automatic routing/failover and a unified key. It can route across multiple providers instead of locking the bot to one model.

OmniRoute / other gateways:
Set AI_PROVIDER=omniroute, put the gateway /v1 URL in AI_BASE_URL, put its key in AI_API_KEY, and use the model value supported by that gateway. The adapter is intentionally OpenAI-compatible so the bot is not hard-coded to one LLM vendor.

Direct DeepSeek fallback:
Set DEEPSEEK_API_KEY and DEEPSEEK_MODEL. If the primary gateway fails, the bot attempts direct DeepSeek. Never commit API keys.

## Windows setup

1. Install MetaTrader 5 desktop and log into the intended account.
2. Enable Algo Trading in MT5 if the broker/account requires it.
3. Clone or download this repository.
4. Double-click setup.bat.
5. Open .env.
6. Keep TRADING_MODE=PAPER and ALLOW_LIVE_TRADING=false for first verification.
7. Change SYMBOLS to your broker's exact symbol names.
8. Configure the LLM gateway.
9. Double-click start.bat.
10. Open http://127.0.0.1:8000.
11. Confirm MT5 CONNECTED, account balance/equity, chart and AI status.
12. Use the dashboard TRADING ON/OFF button to control this bot.

## Going live

First test on a demo account. AI confidence is not a profitability guarantee.

After verifying symbol mapping, SL/TP, sizing and execution:
TRADING_MODE=LIVE
ALLOW_LIVE_TRADING=true

Restart start.bat. Then use TRADING ON in the dashboard.

Recommended starting limits:
RISK_PER_TRADE=0.25
MAX_DAILY_LOSS_PCT=2.0
MAX_DRAWDOWN_PCT=5.0
MAX_OPEN_POSITIONS=3

The dashboard Trading ON/OFF controls this bot's execution permission and persists in SQLite. It does not toggle the MT5 desktop AutoTrading button itself.

## Dashboard

- account balance/equity/free margin/floating P&L
- MT5 connection state
- Trading ON/OFF
- candlestick chart
- configured symbols
- AI signal and reasoning
- open positions
- event feed
- MT5 deal history at /api/history?days=30

## Important

MT5 and broker credentials stay on your PC. Do not paste passwords or API keys into chat or GitHub.

This is an execution tool, not a profit guarantee. Validate on demo before live execution.

## FreeLLMAPI exact setup

Use the FreeLLMAPI project you provided as the bot's primary LLM router. Its official README says the local server exposes an OpenAI-compatible API at `http://localhost:3001/v1`, the Keys page is where provider keys are added, and the dashboard header provides the unified `freellmapi-...` API key. The router can automatically fail over across configured providers/models.

Windows: the project recommends its native Windows `.exe` release. Install/start FreeLLMAPI first, open `http://localhost:3001`, add the provider keys you actually have, configure the fallback chain, then copy the unified key. Keep FreeLLMAPI bound to localhost unless you deliberately need LAN access.

Bot `.env`:
```env
AI_PROVIDER=freellmapi
AI_BASE_URL=http://127.0.0.1:3001/v1
AI_API_KEY=freellmapi-PASTE-YOUR-UNIFIED-KEY-HERE
AI_MODEL=auto
```

Do not put the unified key in GitHub. `.env` is local-only. FreeLLMAPI stores provider keys encrypted at rest and is designed as a local-first single-user router.

Before live trading, verify the bot can complete one test request through `/v1/chat/completions` and that FreeLLMAPI has at least one working provider key/model. If the router is unavailable, the trading bot fails closed to `WAIT` rather than inventing a signal.
