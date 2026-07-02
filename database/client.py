"""MongoDB client lifecycle helpers."""
from __future__ import annotations

from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase


class MongoService:
    """Owns the Motor client and selected database."""
    def __init__(self, uri: str, db_name: str) -> None:
        self.client = AsyncIOMotorClient(uri)
        self.db: AsyncIOMotorDatabase = self.client[db_name]

    def close(self) -> None:
        """Close MongoDB sockets."""
        self.client.close()
