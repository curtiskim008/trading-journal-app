# utils/database.py
import sqlite3
from pathlib import Path

DB_PATH = Path("data/trades.db")

def get_connection():
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row  # allows accessing columns by name
    return conn

def init_db():
    conn = get_connection()
    cur = conn.cursor()

    # Create trades table
    cur.execute("""
        CREATE TABLE IF NOT EXISTS trades (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            trade_date TEXT NOT NULL,
            pair TEXT NOT NULL,
            session TEXT,
            direction TEXT,
            entry_time TEXT,
            exit_time TEXT,
            risk_pct REAL,
            _r REAL,
            outcome TEXT,
            pnl REAL DEFAULT 0.0,
            mistakes TEXT,
            comments TEXT,
            screenshot_path TEXT,
            created_at TEXT NOT NULL
        )
    """)

    # Create settings table (for equity and other configurations)
    cur.execute("""
        CREATE TABLE IF NOT EXISTS settings (
            id INTEGER PRIMARY KEY CHECK (id = 1),
            equity REAL
        )
    """)

    # Ensure default equity row exists
    cur.execute("SELECT COUNT(*) AS count FROM settings")
    count = cur.fetchone()["count"]
    if count == 0:
        cur.execute("INSERT INTO settings (id, equity) VALUES (1, 0.0)")

    conn.commit()
    conn.close()

# ==============================
# CRUD for trades
# ==============================

def insert_trade(trade: dict):
    conn = get_connection()
    cur = conn.cursor()

    # Ensure keys exist
    trade.setdefault("pnl", 0.0)
    trade.setdefault("screenshot_path", None)

    # Fetch current equity
    cur.execute("SELECT equity FROM settings WHERE id=1")
    row = cur.fetchone()
    current_equity = row["equity"] if row else 0.0

    # Calculate risk amount
    risk_amount = trade["risk_pct"] / 100 * current_equity

    # Calculate PnL based on outcome
    outcome_lower = trade["outcome"].lower()
    if outcome_lower == "win":
        trade["pnl"] = trade["_r"] * risk_amount
    elif outcome_lower == "loss":
        trade["pnl"] = -risk_amount
    else:  # breakeven
        trade["pnl"] = 0.0

    # Insert trade
    cur.execute("""
        INSERT INTO trades
        (trade_date, pair, session, direction, entry_time, exit_time, risk_pct, _r, outcome, pnl, mistakes, comments, screenshot_path, created_at)
        VALUES
        (:trade_date, :pair, :session, :direction, :entry_time, :exit_time, :risk_pct, :_r, :outcome, :pnl, :mistakes, :comments, :screenshot_path, :created_at)
    """, trade)

    # Update equity
    new_equity = current_equity + trade["pnl"]
    cur.execute("UPDATE settings SET equity=:equity WHERE id=1", {"equity": new_equity})

    conn.commit()
    conn.close()


def get_trades():
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT * FROM trades ORDER BY id ASC")  # oldest to newest
    rows = cur.fetchall()
    conn.close()
    return [dict(row) for row in rows]

def update_trade(trade_id: int, trade: dict):
    conn = get_connection()
    cur = conn.cursor()
    # Ensure keys exist
    trade.setdefault("pnl", 0.0)
    trade.setdefault("screenshot_path", None)
    cur.execute("""
        UPDATE trades SET
            trade_date=:trade_date,
            pair=:pair,
            session=:session,
            direction=:direction,
            entry_time=:entry_time,
            exit_time=:exit_time,
            risk_pct=:risk_pct,
            _r=:_r,
            outcome=:outcome,
            pnl=:pnl,
            mistakes=:mistakes,
            comments=:comments,
            screenshot_path=:screenshot_path
        WHERE id=:id
    """, {**trade, "id": trade_id})
    conn.commit()
    conn.close()

def delete_trade(trade_id: int):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("DELETE FROM trades WHERE id=:id", {"id": trade_id})
    conn.commit()
    conn.close()

def delete_all_trades():
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("DELETE FROM trades")
    conn.commit()
    conn.close()

# ==============================
# Settings / Equity management
# ==============================

def get_equity_balance():
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT equity FROM settings WHERE id=1")
    row = cur.fetchone()
    conn.close()
    return row["equity"] if row else 0.0

def update_equity_balance(new_balance: float):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("UPDATE settings SET equity=:equity WHERE id=1", {"equity": new_balance})
    conn.commit()
    conn.close()

# ==============================
# Initialize DB on import
# ==============================
init_db()
