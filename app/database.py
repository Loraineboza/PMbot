from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import aiosqlite


class Database:
    def __init__(self) -> None:
        self._conn: aiosqlite.Connection | None = None

    async def connect(self, path: str) -> None:
        Path(path).parent.mkdir(parents=True, exist_ok=True)
        self._conn = await aiosqlite.connect(path)
        self._conn.row_factory = aiosqlite.Row
        await self._conn.execute("PRAGMA foreign_keys = ON")
        await self._conn.execute("PRAGMA journal_mode = WAL")

    @property
    def conn(self) -> aiosqlite.Connection:
        if self._conn is None:
            raise RuntimeError("Database is not connected")
        return self._conn

    async def init(self) -> None:
        await self.conn.executescript(
            """
            CREATE TABLE IF NOT EXISTS users (
                user_id INTEGER PRIMARY KEY,
                username TEXT,
                full_name TEXT,
                language_code TEXT DEFAULT 'ru',
                is_subscribed INTEGER NOT NULL DEFAULT 0,
                is_blocked INTEGER NOT NULL DEFAULT 0,
                created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
                updated_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
                last_seen_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
            );

            CREATE TABLE IF NOT EXISTS events (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                event_type TEXT NOT NULL,
                payload TEXT,
                created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY(user_id) REFERENCES users(user_id) ON DELETE SET NULL
            );

            CREATE INDEX IF NOT EXISTS idx_events_type_payload ON events(event_type, payload);
            CREATE INDEX IF NOT EXISTS idx_events_user ON events(user_id);

            CREATE TABLE IF NOT EXISTS reviews (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                username TEXT,
                rating INTEGER NOT NULL CHECK(rating BETWEEN 1 AND 5),
                text TEXT NOT NULL,
                status TEXT NOT NULL DEFAULT 'pending',
                admin_comment TEXT,
                created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
                moderated_at TEXT,
                FOREIGN KEY(user_id) REFERENCES users(user_id) ON DELETE CASCADE
            );

            CREATE TABLE IF NOT EXISTS support_requests (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                username TEXT,
                text TEXT NOT NULL,
                status TEXT NOT NULL DEFAULT 'new',
                created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY(user_id) REFERENCES users(user_id) ON DELETE CASCADE
            );

            CREATE TABLE IF NOT EXISTS reminders (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                reminder_date TEXT NOT NULL,
                note TEXT,
                is_sent INTEGER NOT NULL DEFAULT 0,
                created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
                sent_at TEXT,
                FOREIGN KEY(user_id) REFERENCES users(user_id) ON DELETE CASCADE
            );

            CREATE INDEX IF NOT EXISTS idx_reminders_due ON reminders(reminder_date, is_sent);

            CREATE TABLE IF NOT EXISTS quiz_results (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                answers_json TEXT NOT NULL,
                recommendation TEXT NOT NULL,
                created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY(user_id) REFERENCES users(user_id) ON DELETE CASCADE
            );
            """
        )
        await self.conn.commit()

    async def close(self) -> None:
        if self._conn is not None:
            await self._conn.close()
            self._conn = None

    async def upsert_user(self, user_id: int, username: str | None, full_name: str, language_code: str | None) -> None:
        await self.conn.execute(
            """
            INSERT INTO users(user_id, username, full_name, language_code)
            VALUES(?, ?, ?, COALESCE(?, 'ru'))
            ON CONFLICT(user_id) DO UPDATE SET
                username=excluded.username,
                full_name=excluded.full_name,
                language_code=COALESCE(excluded.language_code, users.language_code),
                updated_at=CURRENT_TIMESTAMP,
                last_seen_at=CURRENT_TIMESTAMP
            """,
            (user_id, username, full_name, language_code),
        )
        await self.conn.commit()

    async def add_event(self, user_id: int | None, event_type: str, payload: str | None = None) -> None:
        await self.conn.execute(
            "INSERT INTO events(user_id, event_type, payload) VALUES(?, ?, ?)",
            (user_id, event_type, payload),
        )
        await self.conn.commit()

    async def get_user(self, user_id: int) -> aiosqlite.Row | None:
        cur = await self.conn.execute("SELECT * FROM users WHERE user_id = ?", (user_id,))
        return await cur.fetchone()

    async def set_subscription(self, user_id: int, is_subscribed: bool) -> None:
        await self.conn.execute(
            "UPDATE users SET is_subscribed = ?, updated_at = CURRENT_TIMESTAMP WHERE user_id = ?",
            (1 if is_subscribed else 0, user_id),
        )
        await self.conn.commit()

    async def set_blocked(self, user_id: int, is_blocked: bool = True) -> None:
        await self.conn.execute(
            "UPDATE users SET is_blocked = ?, updated_at = CURRENT_TIMESTAMP WHERE user_id = ?",
            (1 if is_blocked else 0, user_id),
        )
        await self.conn.commit()

    async def add_review(self, user_id: int, username: str | None, rating: int, text: str) -> int:
        cur = await self.conn.execute(
            "INSERT INTO reviews(user_id, username, rating, text) VALUES(?, ?, ?, ?)",
            (user_id, username, rating, text),
        )
        await self.conn.commit()
        return int(cur.lastrowid)

    async def list_reviews(self, status: str = "approved", limit: int = 10) -> list[aiosqlite.Row]:
        cur = await self.conn.execute(
            "SELECT * FROM reviews WHERE status = ? ORDER BY created_at DESC LIMIT ?",
            (status, limit),
        )
        return await cur.fetchall()

    async def get_review(self, review_id: int) -> aiosqlite.Row | None:
        cur = await self.conn.execute("SELECT * FROM reviews WHERE id = ?", (review_id,))
        return await cur.fetchone()

    async def moderate_review(self, review_id: int, status: str, admin_comment: str | None = None) -> None:
        await self.conn.execute(
            """
            UPDATE reviews
            SET status = ?, admin_comment = ?, moderated_at = CURRENT_TIMESTAMP
            WHERE id = ?
            """,
            (status, admin_comment, review_id),
        )
        await self.conn.commit()

    async def add_support_request(self, user_id: int, username: str | None, text: str) -> int:
        cur = await self.conn.execute(
            "INSERT INTO support_requests(user_id, username, text) VALUES(?, ?, ?)",
            (user_id, username, text),
        )
        await self.conn.commit()
        return int(cur.lastrowid)

    async def add_reminder(self, user_id: int, reminder_date: str, note: str | None = None) -> int:
        cur = await self.conn.execute(
            "INSERT INTO reminders(user_id, reminder_date, note) VALUES(?, ?, ?)",
            (user_id, reminder_date, note),
        )
        await self.conn.commit()
        return int(cur.lastrowid)

    async def list_active_reminders(self, user_id: int, limit: int = 5) -> list[aiosqlite.Row]:
        cur = await self.conn.execute(
            """
            SELECT * FROM reminders
            WHERE user_id = ? AND is_sent = 0
            ORDER BY reminder_date ASC
            LIMIT ?
            """,
            (user_id, limit),
        )
        return await cur.fetchall()

    async def due_reminders(self, today_iso: str) -> list[aiosqlite.Row]:
        cur = await self.conn.execute(
            """
            SELECT reminders.*, users.is_blocked
            FROM reminders
            JOIN users ON users.user_id = reminders.user_id
            WHERE reminders.is_sent = 0
              AND reminders.reminder_date <= ?
              AND users.is_blocked = 0
            """,
            (today_iso,),
        )
        return await cur.fetchall()

    async def mark_reminder_sent(self, reminder_id: int) -> None:
        await self.conn.execute(
            "UPDATE reminders SET is_sent = 1, sent_at = CURRENT_TIMESTAMP WHERE id = ?",
            (reminder_id,),
        )
        await self.conn.commit()

    async def save_quiz_result(self, user_id: int, answers: dict[str, Any], recommendation: str) -> None:
        await self.conn.execute(
            "INSERT INTO quiz_results(user_id, answers_json, recommendation) VALUES(?, ?, ?)",
            (user_id, json.dumps(answers, ensure_ascii=False), recommendation),
        )
        await self.conn.commit()

    async def subscribed_users(self) -> list[int]:
        cur = await self.conn.execute(
            "SELECT user_id FROM users WHERE is_subscribed = 1 AND is_blocked = 0 ORDER BY created_at ASC"
        )
        rows = await cur.fetchall()
        return [int(row["user_id"]) for row in rows]

    async def stats(self) -> dict[str, Any]:
        async def scalar(query: str, params: tuple[Any, ...] = ()) -> int:
            cur = await self.conn.execute(query, params)
            row = await cur.fetchone()
            return int(row[0] or 0)

        top_cur = await self.conn.execute(
            """
            SELECT payload, COUNT(*) AS cnt
            FROM events
            WHERE event_type = 'callback' AND payload IS NOT NULL
            GROUP BY payload
            ORDER BY cnt DESC
            LIMIT 10
            """
        )
        top_buttons = await top_cur.fetchall()
        return {
            "users": await scalar("SELECT COUNT(*) FROM users"),
            "subscribed": await scalar("SELECT COUNT(*) FROM users WHERE is_subscribed = 1"),
            "blocked": await scalar("SELECT COUNT(*) FROM users WHERE is_blocked = 1"),
            "pending_reviews": await scalar("SELECT COUNT(*) FROM reviews WHERE status = 'pending'"),
            "approved_reviews": await scalar("SELECT COUNT(*) FROM reviews WHERE status = 'approved'"),
            "support_new": await scalar("SELECT COUNT(*) FROM support_requests WHERE status = 'new'"),
            "registration_clicks": await scalar(
                "SELECT COUNT(*) FROM events WHERE event_type = 'conversion' AND payload = 'registration_click'"
            ),
            "quiz_finished": await scalar("SELECT COUNT(*) FROM quiz_results"),
            "top_buttons": [(row["payload"], int(row["cnt"])) for row in top_buttons],
        }


# Для PostgreSQL позже можно заменить этот класс на SQLAlchemy async engine
# или asyncpg-репозиторий, сохранив публичные методы выше.
db = Database()

