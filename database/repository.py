"""Async repository for relationship-bot collections."""
from __future__ import annotations

from typing import Any

try:
    import discord
except ModuleNotFoundError:
    discord = None  # type: ignore

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
