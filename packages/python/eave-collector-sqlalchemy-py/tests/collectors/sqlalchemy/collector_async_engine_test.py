import os
import unittest.mock
import uuid
from datetime import datetime
from uuid import UUID

import sqlalchemy
from sqlalchemy import func, text
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column

from eave.collectors.core.datastructures import DatabaseEventPayload, DatabaseOperation, EventPayload, EventType
from eave.collectors.core.write_queue import BatchWriteQueue, QueueParams
from eave.collectors.sqlalchemy.private.collector import SQLAlchemyCollector


class ConsoleOutputBatchWriteQueue(BatchWriteQueue):
    _running: bool = False
    queue: list[EventPayload]

    def __init__(self) -> None:
        super().__init__(queue_params=QueueParams(event_type=EventType.dbevent))
        self.queue = []

    def start_autoflush(self) -> None:
        self._running = True

    def stop_autoflush(self) -> None:
        self._running = False

    def put(self, payload: EventPayload) -> None:
        if not self._running:
            raise RuntimeError("queue processor not running")

        self.queue.append(payload)


db_uri = sqlalchemy.engine.url.URL.create(
    drivername="postgresql+asyncpg",
    host=os.getenv("EAVE_DB_HOST", "localhost"),
    port=int(os.getenv("EAVE_DB_PORT", "5432")),
    username=os.getenv("EAVE_DB_USER", None),
    password=os.getenv("EAVE_DB_PASS", None),
    database=os.getenv("EAVE_DB_NAME", "eave-sqlalchemy-tests"),
)

async_engine = create_async_engine(
    db_uri,
    echo=False,
    connect_args={
        "server_settings": {
            "timezone": "UTC",
        },
    },
)

async_session = async_sessionmaker(async_engine)


class OrmBase(DeclarativeBase):
    pass


class PeopleOrm(OrmBase):
    __tablename__ = "people"

    id: Mapped[UUID] = mapped_column(primary_key=True, server_default=text("(gen_random_uuid())"))
    name: Mapped[str]
    created: Mapped[datetime] = mapped_column(server_default=func.current_timestamp())
    updated: Mapped[datetime | None] = mapped_column(server_default=None, onupdate=func.current_timestamp())


class CollectorTestBase(unittest.IsolatedAsyncioTestCase):
    async def asyncSetUp(self) -> None:
        await super().asyncSetUp()

        async with async_engine.begin() as connection:
            await connection.run_sync(OrmBase.metadata.drop_all)
            await connection.run_sync(OrmBase.metadata.create_all)

        self._collector = SQLAlchemyCollector()
        self._write_queue = ConsoleOutputBatchWriteQueue()
        self._collector.write_queue = self._write_queue
        await self._collector.start(engine=async_engine)

    async def test_after_execute_insert(self) -> None:
        assert len(self._write_queue.queue) == 0
        person_name = uuid.uuid4().hex

        async with async_session.begin() as session:
            team = PeopleOrm(name=person_name)
            session.add(team)

        assert len(self._write_queue.queue) == 1
        e = self._write_queue.queue[0]
        assert isinstance(e, DatabaseEventPayload)
        assert e.table_name == "people"
        assert e.operation == DatabaseOperation.INSERT
        assert e.db_name == db_uri.database
        assert e.parameters is not None
        assert e.parameters["name"] == person_name
        assert "__primary_key" in e.parameters

    async def test_after_execute_update(self) -> None:
        assert len(self._write_queue.queue) == 0
        person_name = uuid.uuid4().hex

        async with async_session.begin() as session:
            team = PeopleOrm(name=person_name)
            session.add(team)

        assert len(self._write_queue.queue) == 1
        e0 = self._write_queue.queue[0]
        assert isinstance(e0, DatabaseEventPayload)
        assert e0.parameters is not None

        async with async_session.begin() as session:
            r = await session.get_one(entity=PeopleOrm, ident=tuple(e0.parameters["__primary_key"]))
            new_person_name = uuid.uuid4().hex
            r.name = new_person_name

        assert len(self._write_queue.queue) == 2
        e = self._write_queue.queue[1]
        assert isinstance(e, DatabaseEventPayload)
        assert e.table_name == "people"
        assert e.operation == DatabaseOperation.UPDATE
        assert e.db_name == db_uri.database
        assert e.parameters is not None
        assert e.parameters["name"] == new_person_name
