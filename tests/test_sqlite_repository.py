import asyncio

from database.sqlite_repository import SQLiteRelationshipRepository


def test_sqlite_repository_preserves_core_behavior(tmp_path):
    async def run():
        repo = SQLiteRelationshipRepository(str(tmp_path / "relationship.sqlite3"))
        await repo.ensure_indexes()
        await repo.ensure_indexes()

        await repo.create("memories", {"author_id": 1, "text": "movie night", "tags": ["movies"]})
        await repo.create("trackers", {"kind": "movie", "title": "Your Name", "status": "planned"})
        await repo.set_logging_channel(123, 456)

        memories = await repo.recent("memories")
        stats = await repo.stats()

        assert memories[0]["text"] == "movie night"
        assert stats["memories"] == 1
        assert stats["shared items"] == 1
        assert await repo.get_logging_channel_id(123) == 456
        repo.close()

    asyncio.run(run())
