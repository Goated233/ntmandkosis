"""Async repository for relationship-bot collections.

Index creation is intentionally resilient for Railway/free-tier MongoDB deployments:
nonessential index builds are skipped when MongoDB reports OutOfDiskSpace, while
all other database errors still fail fast.
"""
from __future__ import annotations

import logging
"""Async repository for relationship-bot collections."""
from __future__ import annotations

from typing import Any

try:
    import discord
except ModuleNotFoundError:
    discord = None  # type: ignore

try:
    from motor.motor_asyncio import AsyncIOMotorDatabase
except ModuleNotFoundError:  # pragma: no cover - typing fallback for minimal test envs
    AsyncIOMotorDatabase = Any  # type: ignore

try:
    from pymongo.errors import OperationFailure
except ModuleNotFoundError:  # pragma: no cover - motor installs pymongo in production
    class OperationFailure(Exception):  # type: ignore[no-redef]
        """Fallback OperationFailure when pymongo is unavailable in unit tests."""

        def __init__(self, message: str = "", details: dict[str, Any] | None = None) -> None:
            super().__init__(message)
            self.details = details or {}

from utils.time import utcnow

LOGGER = logging.getLogger(__name__)

CORE_INDEXES: tuple[tuple[str, str, Any, dict[str, Any]], ...] = (
    ("users", "user_id_unique", "user_id", {"unique": True}),
    ("settings", "guild_id_unique", "guild_id", {"unique": True}),
    ("memories", "created_at_desc", [("created_at", -1)], {}),
    ("complaints", "author_status_created", [("author_id", 1), ("status", 1), ("created_at", -1)], {}),
    ("checkins", "author_created", [("author_id", 1), ("created_at", -1)], {}),
    ("goals", "created_at_desc", [("created_at", -1)], {}),
    ("trackers", "kind_status_created", [("kind", 1), ("status", 1), ("created_at", -1)], {}),
    ("journals", "created_at_desc", [("created_at", -1)], {}),
    # Temporary operational logs are safe to expire and reduce storage usage.
    ("bot_events", "created_at_ttl_30d", [("created_at", 1)], {"expireAfterSeconds": 60 * 60 * 24 * 30}),
)


class RelationshipRepository:
    """High-level MongoDB operations used by cogs and services."""

    def __init__(self, db: AsyncIOMotorDatabase) -> None:
        self.db = db
        self._indexes_ensured = False
        self.indexes_skipped_reason: str | None = None

    async def ensure_indexes(self) -> None:
        """Create required indexes once, skipping only free-tier disk failures.

        Startup must not perform writes other than idempotent index maintenance.
        If MongoDB is out of disk space, the bot can still run with degraded query
        performance; normal user writes may still fail until the database has
        enough free disk space.
        """
        if self._indexes_ensured:
            LOGGER.info("MongoDB index initialization already completed; skipping duplicate startup attempt.")
            return

        attempted = 0
        skipped_existing = 0
        for collection_name, index_name, keys, options in CORE_INDEXES:
            created, existed = await self._create_index_if_missing(collection_name, index_name, keys, options)
            attempted += int(created)
            skipped_existing += int(existed)

        self._indexes_ensured = True
        LOGGER.info(
            "MongoDB index initialization finished",
            extra={"indexes_created": attempted, "indexes_already_present": skipped_existing, "indexes_skipped_reason": self.indexes_skipped_reason},
        )

    async def _create_index_if_missing(self, collection_name: str, index_name: str, keys: Any, options: dict[str, Any]) -> tuple[bool, bool]:
        """Create one named index if it does not already exist."""
        collection = self.db[collection_name]
        existing = await collection.index_information()
        if index_name in existing:
            LOGGER.debug("MongoDB index already exists", extra={"collection": collection_name, "index": index_name})
            return False, True
        try:
            await collection.create_index(keys, name=index_name, **options)
            LOGGER.info("MongoDB index created", extra={"collection": collection_name, "index": index_name})
            return True, False
        except OperationFailure as exc:
            if self._is_out_of_disk_space(exc):
                self.indexes_skipped_reason = "OutOfDiskSpace"
                LOGGER.warning(
                    "Skipping MongoDB index creation because the database reported OutOfDiskSpace; startup will continue with degraded query performance. Free disk space or compact/clear old data to restore index creation.",
                    extra={"collection": collection_name, "index": index_name, "codeName": self._operation_code_name(exc), "error": str(exc)},
                )
                return False, False
            raise

    def _is_out_of_disk_space(self, exc: OperationFailure) -> bool:
        """Return whether an OperationFailure is MongoDB OutOfDiskSpace."""
        code_name = self._operation_code_name(exc)
        return code_name == "OutOfDiskSpace" or "OutOfDiskSpace" in str(exc)

    def _operation_code_name(self, exc: OperationFailure) -> str | None:
        """Extract the MongoDB codeName from an OperationFailure."""
        details = getattr(exc, "details", None) or {}
        value = details.get("codeName")
        return str(value) if value else None
from motor.motor_asyncio import AsyncIOMotorDatabase

from utils.time import utcnow


class RelationshipRepository:
    """High-level MongoDB operations used by cogs and services."""
    def __init__(self, db: AsyncIOMotorDatabase) -> None:
        self.db = db

    async def ensure_indexes(self) -> None:
        """Create production indexes for common relationship queries."""
        await self.db.users.create_index("user_id", unique=True)
        for name in ["memories", "complaints", "checkins", "goals", "trackers", "journals"]:
            await self.db[name].create_index([("created_at", -1)])
        await self.db.trackers.create_index([("kind", 1), ("status", 1), ("created_at", -1)])
        await self.db.complaints.create_index([("author_id", 1), ("status", 1), ("created_at", -1)])
        await self.db.checkins.create_index([("author_id", 1), ("created_at", -1)])
        await self.db.settings.create_index("guild_id", unique=True)
        for name in ["gratitude", "affirmations", "notes", "boundaries", "triggers", "needs", "playlist", "wishlist", "gifts", "achievements", "inside_jokes", "favorites", "dreams", "plans", "countdowns", "mood_notes", "lessons", "patterns", "reflections"]:
            await self.db[name].create_index([("created_at", -1)])

    async def upsert_user(self, user_id: int, display_name: str) -> None:
        """Insert or update a Discord user."""
        await self.db.users.update_one(
            {"user_id": user_id},
            {"$set": {"display_name": display_name, "updated_at": utcnow()}, "$setOnInsert": {"created_at": utcnow()}},
            upsert=True,
        )

    async def create(self, collection: str, document: dict[str, Any]) -> dict[str, Any]:
        """Insert a document and return it with its generated ID."""
        document.setdefault("created_at", utcnow())
        result = await self.db[collection].insert_one(document)
        document["_id"] = result.inserted_id
        return document

    async def recent(self, collection: str, *, limit: int = 10, query: dict[str, Any] | None = None) -> list[dict[str, Any]]:
        """Return recent documents from a collection."""
        cursor = self.db[collection].find(query or {}).sort("created_at", -1).limit(limit)
        return [doc async for doc in cursor]

    async def stats(self) -> dict[str, int]:
        """Return communication and tracking counts."""
        keys = {"memories": "memories", "complaints": "concerns", "checkins": "check-ins", "goals": "goals", "trackers": "shared items"}
        return {label: await self.db[col].count_documents({}) for col, label in keys.items()}

    async def set_logging_channel(self, guild_id: int, channel_id: int) -> None:
        """Persist the logging channel for a server."""
        await self.db.settings.update_one({"guild_id": guild_id}, {"$set": {"logging_channel_id": channel_id, "updated_at": utcnow()}, "$setOnInsert": {"created_at": utcnow()}}, upsert=True)

    async def get_logging_channel_id(self, guild_id: int) -> int | None:
        """Return a configured logging channel ID for a server."""
        document = await self.db.settings.find_one({"guild_id": guild_id})
        return int(document["logging_channel_id"]) if document and document.get("logging_channel_id") else None

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
