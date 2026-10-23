from __future__ import annotations
import json,sqlite3
from datetime import datetime,timezone
from .config import DB_PATH
def conn():
    c=sqlite3.connect(DB_PATH); c.row_factory=sqlite3.Row; return c
def init_db():
    with conn() as c:
        c.execute("CREATE TABLE IF NOT EXISTS settings (key TEXT PRIMARY KEY,value TEXT NOT NULL)")
        c.execute("CREATE TABLE IF NOT EXISTS events (id INTEGER PRIMARY KEY AUTOINCREMENT,created_at TEXT NOT NULL,kind TEXT NOT NULL,symbol TEXT,payload TEXT NOT NULL)")
        c.execute("CREATE TABLE IF NOT EXISTS signals (id INTEGER PRIMARY KEY AUTOINCREMENT,created_at TEXT NOT NULL,symbol TEXT NOT NULL,signal TEXT NOT NULL,confidence REAL,entry REAL,stop_loss REAL,take_profit REAL,logic TEXT,payload TEXT NOT NULL)")
        c.execute("CREATE TABLE IF NOT EXISTS executions (id INTEGER PRIMARY KEY AUTOINCREMENT,created_at TEXT NOT NULL,symbol TEXT NOT NULL,status TEXT NOT NULL,order_id TEXT,deal_id TEXT,payload TEXT NOT NULL)")
        c.execute("INSERT OR IGNORE INTO settings(key,value) VALUES('trading_enabled','0')")
        c.commit()
def get_setting(key,default=None):
    with conn() as c:
        row=c.execute("SELECT value FROM settings WHERE key=?",(key,)).fetchone()
        return row["value"] if row else default
def set_setting(key,value):
    with conn() as c:
        c.execute("INSERT INTO settings(key,value) VALUES(?,?) ON CONFLICT(key) DO UPDATE SET value=excluded.value",(key,str(value))); c.commit()
def log_event(kind,payload,symbol=None):
    with conn() as c:
        c.execute("INSERT INTO events(created_at,kind,symbol,payload) VALUES(?,?,?,?)",(datetime.now(timezone.utc).isoformat(),kind,symbol,json.dumps(payload,default=str))); c.commit()
def log_signal(symbol,signal):
    with conn() as c:
        c.execute("INSERT INTO signals(created_at,symbol,signal,confidence,entry,stop_loss,take_profit,logic,payload) VALUES(?,?,?,?,?,?,?,?,?)",(datetime.now(timezone.utc).isoformat(),symbol,signal.get("signal","WAIT"),signal.get("confidence"),signal.get("entry"),signal.get("stop_loss"),signal.get("take_profit"),signal.get("logic",""),json.dumps(signal,default=str))); c.commit()
def log_execution(symbol,result):
    with conn() as c:
        c.execute("INSERT INTO executions(created_at,symbol,status,order_id,deal_id,payload) VALUES(?,?,?,?,?,?)",(datetime.now(timezone.utc).isoformat(),symbol,str(result.get("status")),str(result.get("order") or ""),str(result.get("deal") or ""),json.dumps(result,default=str))); c.commit()
def recent_events(limit=50):
    with conn() as c: rows=c.execute("SELECT created_at,kind,symbol,payload FROM events ORDER BY id DESC LIMIT ?",(limit,)).fetchall()
    return [{"time":r["created_at"],"kind":r["kind"],"symbol":r["symbol"],**json.loads(r["payload"])} for r in rows]
def last_execution_time(symbol):
    with conn() as c: row=c.execute("SELECT created_at FROM executions WHERE symbol=? ORDER BY id DESC LIMIT 1",(symbol,)).fetchone()
    return datetime.fromisoformat(row["created_at"]) if row else None
