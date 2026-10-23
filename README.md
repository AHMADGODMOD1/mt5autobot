# MT5 AI Autobot

Institutional-style MT5 AI trading system scaffold.

## Architecture
- MT5 local terminal and broker data
- FastAPI backend
- Multi-timeframe market data
- AI signal layer
- Risk engine with veto controls
- Execution layer
- Live dashboard
- Trade journal

## Safety
Default mode is PAPER. Live execution must be explicitly enabled in local environment configuration.

## Run locally
1. Install Python 3.11+.
2. `pip install -r requirements.txt`
3. Copy `.env.example` to `.env` and configure local credentials.
4. Start MT5 and log into the desired account.
5. `python -m uvicorn app.main:app --host 127.0.0.1 --port 8000`
