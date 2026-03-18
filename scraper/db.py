import sqlite3
import os

DB_PATH = "data/odds.db"

def get_conn():
    os.makedirs("data", exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row  # lets you access columns by name
    return conn

def init_db():
    """Create tables if they don't exist yet."""
    with get_conn() as conn:
        conn.executescript("""
            CREATE TABLE IF NOT EXISTS odds_snapshots (
                id          INTEGER PRIMARY KEY AUTOINCREMENT,
                game_id     TEXT    NOT NULL,
                sport       TEXT    NOT NULL,
                home_team   TEXT    NOT NULL,
                away_team   TEXT    NOT NULL,
                commence    DATETIME,
                bookmaker   TEXT    NOT NULL,
                market      TEXT    NOT NULL,
                label       TEXT,
                point       REAL,
                price       REAL,
                captured_at DATETIME DEFAULT (datetime('now'))
            );

            CREATE TABLE IF NOT EXISTS poll_log (
                id          INTEGER PRIMARY KEY AUTOINCREMENT,
                source      TEXT,
                credits_used INTEGER,
                status      TEXT,
                polled_at   DATETIME DEFAULT (datetime('now'))
            );
        """)
    print("Database initialized.")

def insert_snapshots(rows: list[dict]):
    """Insert a batch of snapshot rows."""
    sql = """
        INSERT INTO odds_snapshots
            (game_id, sport, home_team, away_team, commence,
             bookmaker, market, label, point, price)
        VALUES
            (:game_id, :sport, :home_team, :away_team, :commence,
             :bookmaker, :market, :label, :point, :price)
    """
    with get_conn() as conn:
        conn.executemany(sql, rows)

def log_poll(source: str, credits_used: int, status: str):
    with get_conn() as conn:
        conn.execute(
            "INSERT INTO poll_log (source, credits_used, status) VALUES (?,?,?)",
            (source, credits_used, status)
        )