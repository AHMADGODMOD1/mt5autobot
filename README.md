# MT5 AI Autobot

Windows-first MT5 AI trading bot. It does **not** store or request your broker login, broker password, or server. The Python MT5 integration calls `mt5.initialize()`, which finds/starts MetaTrader 5 and connects to the account already active/saved in the terminal.

## Simple flow

1. MetaTrader 5 is installed on Windows.
2. You log in to the account inside MT5 itself.
3. The bot starts and calls `mt5.initialize()`.
4. It reads the currently active account with `account_info()`.
5. It checks MT5/account trading permissions before any live order.
6. Market data from D1/H4/H1/M15/M5 is sent to the online AI endpoint.
7. AI returns BUY / SELL / WAIT + SL / TP.
8. Risk engine validates the trade and calculates size.
9. Only then can the order be sent to the already logged-in MT5 account.

## AI: simple online setup

FreeLLMAPI and OmniRoute are no longer required.

Default:
```env
AI_PROVIDER=openrouter
AI_BASE_URL=https://openrouter.ai/api/v1
AI_MODEL=openai/gpt-oss-120b:free
AI_API_KEY=
```

This uses OpenAI's open-weight GPT-OSS 120B through OpenRouter's online free endpoint. OpenRouter free usage is rate-limited, so it is suitable for testing/light use rather than guaranteed production capacity.

Create one OpenRouter API key and paste it only into your local `.env`. Never commit or send the key in chat.

## MT5 credentials

There are deliberately **no** settings for:
- MT5 login
- MT5 password
- broker server

The bot uses the account already logged in inside the MetaTrader 5 Windows terminal. If MT5 is closed, `mt5.initialize()` can launch/find the installed terminal.

Before LIVE execution the bot checks:
- terminal connected
- MT5 Algo Trading permission
- Python trade API not disabled
- account trading allowed
- account expert trading allowed

If these checks fail, live execution is blocked.

## Windows setup

1. Install MetaTrader 5 and log in normally inside MT5.
2. Clone/download this repository.
3. Double-click `setup.bat`.
4. Open the generated `.env`.
5. Put only your OpenRouter API key in `AI_API_KEY`.
6. Set `SYMBOLS` to the exact symbols used by your broker.
7. Keep `TRADING_MODE=PAPER` and `ALLOW_LIVE_TRADING=false` for the first test.
8. Double-click `start.bat`.
9. Open `http://127.0.0.1:8000`.
10. Confirm the dashboard shows the correct MT5 login/server/balance and Algo Trading readiness.

## Live mode

Only after demo/PAPER verification:
```env
TRADING_MODE=LIVE
ALLOW_LIVE_TRADING=true
```

Restart `start.bat`, make sure Algo Trading is enabled in MT5, then press **TRADING ON** in the dashboard.

The dashboard button controls this bot. It does not secretly enable MT5's Algo Trading setting. If MT5 Algo Trading is OFF, the bot refuses to send live orders.

## Risk defaults

```env
RISK_PER_TRADE=0.25
MAX_DAILY_LOSS_PCT=2.0
MAX_DRAWDOWN_PCT=5.0
MAX_OPEN_POSITIONS=3
MAX_SPREAD_POINTS=80
MIN_AI_CONFIDENCE=70
```

The bot also has entry cooldown, duplicate-direction protection, broker volume normalization and `order_check()` before `order_send()`.

## Important

AI output is not a profit guarantee. Test on demo first. Free online inference can be unavailable or rate-limited; when the AI endpoint fails, the bot fails closed to **WAIT** rather than inventing a signal.
