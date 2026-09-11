"""Database layer — logs every scored transaction for an audit trail."""
import sqlite3
from datetime import datetime

DB_PATH = "fraud_logs.db"

def init_db():
    conn = sqlite3.connect(DB_PATH)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS transaction_logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id TEXT, amount REAL, hour INTEGER, is_flagged INTEGER,
            fraud_probability REAL, model_used TEXT, scored_at TEXT
        )
    """)
    conn.commit()
    conn.close()

def log_transaction(user_id, amount, hour, is_flagged, fraud_probability, model_used):
    conn = sqlite3.connect(DB_PATH)
    conn.execute(
        "INSERT INTO transaction_logs (user_id, amount, hour, is_flagged, fraud_probability, model_used, scored_at) "
        "VALUES (?, ?, ?, ?, ?, ?, ?)",
        (user_id, amount, hour, is_flagged, fraud_probability, model_used, datetime.utcnow().isoformat())
    )
    conn.commit()
    conn.close()

def get_recent_logs(limit=50):
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    rows = conn.execute("SELECT * FROM transaction_logs ORDER BY id DESC LIMIT ?", (limit,)).fetchall()
    conn.close()
    return [dict(r) for r in rows]

def get_stats():
    conn = sqlite3.connect(DB_PATH)
    total = conn.execute("SELECT COUNT(*) FROM transaction_logs").fetchone()[0]
    flagged = conn.execute("SELECT COUNT(*) FROM transaction_logs WHERE is_flagged = 1").fetchone()[0]
    conn.close()
    return {"total_scored": total, "total_flagged": flagged}
