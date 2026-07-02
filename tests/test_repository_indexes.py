import asyncio

from database.repository import CORE_INDEXES, OperationFailure, RelationshipRepository


class FakeCollection:
    def __init__(self, *, fail_index: str | None = None, existing: set[str] | None = None):
        self.fail_index = fail_index
        self.indexes = {name: {} for name in (existing or set())}
        self.created = []

    async def index_information(self):
        return self.indexes

    async def create_index(self, keys, name, **options):
        if name == self.fail_index:
            raise OperationFailure("available disk space is less than required minimum: OutOfDiskSpace", details={"codeName": "OutOfDiskSpace"})
        self.indexes[name] = {"key": keys, **options}
        self.created.append(name)
        return name


class FakeDB:
    def __init__(self, *, fail_index: str | None = None, existing: set[str] | None = None):
        self.collections = {}
        self.fail_index = fail_index
        self.existing = existing or set()

    def __getitem__(self, name):
        if name not in self.collections:
            self.collections[name] = FakeCollection(fail_index=self.fail_index, existing=self.existing)
        return self.collections[name]


def test_indexes_skip_out_of_disk_and_continue():
    async def run():
        repo = RelationshipRepository(FakeDB(fail_index="created_at_desc"))

        await repo.ensure_indexes()

        assert repo.indexes_skipped_reason == "OutOfDiskSpace"
        assert repo._indexes_ensured is True

    asyncio.run(run())


def test_indexes_attempted_only_once():
    async def run():
        repo = RelationshipRepository(FakeDB())

        await repo.ensure_indexes()
        first_count = sum(len(collection.created) for collection in repo.db.collections.values())
        await repo.ensure_indexes()
        second_count = sum(len(collection.created) for collection in repo.db.collections.values())

        assert first_count == len(CORE_INDEXES)
        assert second_count == first_count

    asyncio.run(run())


def test_existing_indexes_are_not_recreated():
    async def run():
        existing = {index_name for _, index_name, _, _ in CORE_INDEXES}
        repo = RelationshipRepository(FakeDB(existing=existing))

        await repo.ensure_indexes()

        assert sum(len(collection.created) for collection in repo.db.collections.values()) == 0

    asyncio.run(run())
