import logging
import sqlite3
from typing import Self

_DB_NAME = "output/market_data.db"


logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)


class Store:
    def __init__(self):
        self.con = self.init_db()

    @staticmethod
    def _new_connection() -> sqlite3.Connection:
        return sqlite3.connect(_DB_NAME)

    def save_event(self: Self, integration: str, event: str):
        con = self.con
        cur = con.cursor()
        cur.execute(
            """
            INSERT INTO events (integration, event)
            VALUES (?, ?)
            """,
            (integration, event),
        )
        con.commit()

    def close(self: Self) -> None:
        self.con.close()

    def get_summary(self: Self):
        con = self._new_connection()
        cur = con.cursor()
        cur.execute(
            """
            SELECT integration, COUNT(*) as event_count
            FROM events
            GROUP BY integration
            """
        )
        summary = cur.fetchall()
        con.close()
        return summary

    @staticmethod
    def init_db() -> sqlite3.Connection:
        con = sqlite3.connect(_DB_NAME)
        cur = con.cursor()
        cur.execute(
            """
            CREATE TABLE IF NOT EXISTS events (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                integration TEXT NOT NULL,
                event TEXT
            )
            """
        )
        con.commit()
        return con
