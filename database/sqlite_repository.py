"""SQLite repository for Railway deployments without external MongoDB storage.

This repository preserves the async interface used by the Discord cogs while using
Python's built-in sqlite3 module. It avoids external database volumes entirely,
which is useful when a Railway MongoDB free-tier volume is full.
"""
from __future__ import annotations

import json
import logging
import sqlite3
from pathlib import Path
from typing import Any

try:
    import discord
except ModuleNotFoundError:
    discord = None  # type: ignore

from utils.time import utcnow

LOGGER = logging.getLogger(__name__)

CORE_TABLES = (
    "users",
    "settings",
    "memories",
    "complaints",
    "checkins",
    "goals",
    "trackers",
    "journals",
    "bot_events",
    "gratitude",
    "affirmations",
    "notes",
    "boundaries",
    "triggers",
    "needs",
    "playlist",
    "wishlist",
    "gifts",
    "achievements",
    "inside_jokes",
    "favorites",
    "dreams",
    "plans",
    "countdowns",
    "mood_notes",
    "lessons",
    "patterns",
    "reflections",
)


class SQLiteRelationshipRepository:
    """SQLite-backed repository with the same public methods as Mongo storage."""

    def __init__(self, path: str) -> None:
        self.path = Path(path)
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self.connection = sqlite3.connect(self.path)
        self.connection.row_factory = sqlite3.Row
        self._indexes_ensured = False

    async def ensure_indexes(self) -> None:
        """Create SQLite tables and indexes once during startup."""
        if self._indexes_ensured:
            LOGGER.info("SQLite schema already initialized; skipping duplicate startup attempt.")
            return
        cursor = self.connection.cursor()
        for table in CORE_TABLES:
            cursor.execute(
                f"""
                CREATE TABLE IF NOT EXISTS {table} (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    created_at TEXT NOT NULL,
                    data TEXT NOT NULL
                )
                """
            )
            cursor.execute(f"CREATE INDEX IF NOT EXISTS idx_{table}_created_at ON {table}(created_at)")
        cursor.execute("CREATE UNIQUE INDEX IF NOT EXISTS idx_users_user_id ON users(json_extract(data, '$.user_id'))")
        cursor.execute("CREATE UNIQUE INDEX IF NOT EXISTS idx_settings_guild_id ON settings(json_extract(data, '$.guild_id'))")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_trackers_kind_status ON trackers(json_extract(data, '$.kind'), json_extract(data, '$.status'), created_at)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_complaints_author_status ON complaints(json_extract(data, '$.author_id'), json_extract(data, '$.status'), created_at)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_checkins_author ON checkins(json_extract(data, '$.author_id'), created_at)")
        self.connection.commit()
        self._indexes_ensured = True
        LOGGER.info("SQLite schema initialization finished", extra={"sqlite_path": str(self.path)})

    async def upsert_user(self, user_id: int, display_name: str) -> None:
        """Insert or update a Discord user."""
        await self._upsert_json("users", "user_id", user_id, {"user_id": user_id, "display_name": display_name, "updated_at": utcnow().isoformat()})

    async def create(self, collection: str, document: dict[str, Any]) -> dict[str, Any]:
        """Insert a document and return it with its generated ID."""
        self._ensure_known_table(collection)
        created_at = self._string_time(document.setdefault("created_at", utcnow()))
        document["created_at"] = created_at
        cursor = self.connection.execute(
            f"INSERT INTO {collection} (created_at, data) VALUES (?, ?)",
            (created_at, json.dumps(document, default=str)),
        )
        self.connection.commit()
        document["_id"] = cursor.lastrowid
        return document

    async def recent(self, collection: str, *, limit: int = 10, query: dict[str, Any] | None = None) -> list[dict[str, Any]]:
        """Return recent documents from a collection."""
        self._ensure_known_table(collection)
        sql = f"SELECT id, data FROM {collection}"
        params: list[Any] = []
        if query:
            clauses = []
            for key, value in query.items():
                clauses.append(f"json_extract(data, '$.{key}') = ?")
                params.append(value)
            sql += " WHERE " + " AND ".join(clauses)
        sql += " ORDER BY created_at DESC LIMIT ?"
        params.append(limit)
        rows = self.connection.execute(sql, params).fetchall()
        return [self._row_to_document(row) for row in rows]

    async def stats(self) -> dict[str, int]:
        """Return communication and tracking counts."""
        keys = {"memories": "memories", "complaints": "concerns", "checkins": "check-ins", "goals": "goals", "trackers": "shared items"}
        return {label: self.connection.execute(f"SELECT COUNT(*) FROM {table}").fetchone()[0] for table, label in keys.items()}

    async def set_logging_channel(self, guild_id: int, channel_id: int) -> None:
        """Persist the logging channel for a server."""
        await self._upsert_json("settings", "guild_id", guild_id, {"guild_id": guild_id, "logging_channel_id": channel_id, "updated_at": utcnow().isoformat()})

    async def get_logging_channel_id(self, guild_id: int) -> int | None:
        """Return a configured logging channel ID for a server."""
        rows = await self.recent("settings", limit=1, query={"guild_id": guild_id})
        value = rows[0].get("logging_channel_id") if rows else None
        return int(value) if value else None

    async def log_event(self, bot: Any, guild_id: int, title: str, message: str) -> None:
        """Send an operational event to the configured Discord log channel."""
        channel_id = await self.get_logging_channel_id(guild_id)
        if not channel_id:
            return
        channel = bot.get_channel(channel_id)
        if channel is None:
            return
        if discord is None:
            await channel.send(f"**{title}**\n{message}")
            return
        embed = discord.Embed(title=title, description=message, color=0xB8A6F6)
        embed.set_footer(text="Relationship bot logs")
        await channel.send(embed=embed)

    def close(self) -> None:
        """Close the SQLite connection."""
        self.connection.close()

    async def _upsert_json(self, table: str, key: str, value: Any, document: dict[str, Any]) -> None:
        """Upsert one JSON document by a JSON key."""
        self._ensure_known_table(table)
        created_at = self._string_time(document.setdefault("created_at", utcnow()))
        document["created_at"] = created_at
        existing = self.connection.execute(f"SELECT id FROM {table} WHERE json_extract(data, '$.{key}') = ? LIMIT 1", (value,)).fetchone()
        payload = json.dumps(document, default=str)
        if existing:
            self.connection.execute(f"UPDATE {table} SET data = ? WHERE id = ?", (payload, existing["id"]))
        else:
            self.connection.execute(f"INSERT INTO {table} (created_at, data) VALUES (?, ?)", (created_at, payload))
        self.connection.commit()

    def _row_to_document(self, row: sqlite3.Row) -> dict[str, Any]:
        """Convert a SQLite row into a document-like dictionary."""
        document = json.loads(row["data"])
        document.setdefault("_id", row["id"])
        return document

    def _ensure_known_table(self, collection: str) -> None:
        """Reject unknown table names to keep SQL construction safe."""
        if collection not in CORE_TABLES:
            raise ValueError(f"Unknown SQLite collection: {collection}")

    def _string_time(self, value: Any) -> str:
        """Serialize datetime-like values for SQLite ordering."""
        return value.isoformat() if hasattr(value, "isoformat") else str(value)
