import logging
import sqlite3
from typing import Self

from market_analytics_platform.models import Event

_DB_NAME = "output/market_data.db"


logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)


class Store:
    def __init__(self):
        self.con = self.init_db()

    @staticmethod
    def _new_connection() -> sqlite3.Connection:
        return sqlite3.connect(_DB_NAME)

    def save(self: Self, event: Event):
        con = self.con
        cur = con.cursor()
        cur.execute(
            """
            INSERT INTO events (integration, event, channel, instrument_id)
            VALUES (?, ?, ?, ?)
            """,
            (event.integration, event.payload, event.channel, event.instrument_id),
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
        self.close()
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
                event TEXT,
                channel TEXT NULL,
                instrument_id TEXT NULL
            )
            """
        )
        con.commit()
        return con
