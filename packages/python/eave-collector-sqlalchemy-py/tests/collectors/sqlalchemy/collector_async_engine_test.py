import os
import unittest.mock
import uuid
from datetime import datetime
from uuid import UUID

import sqlalchemy
from sqlalchemy import NullPool, func, text
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column

from eave.collectors.core.correlation_context import CORR_CTX
from eave.collectors.core.datastructures import DatabaseEventPayload, DatabaseOperation
from eave.collectors.core.test_util import EphemeralWriteQueue
from eave.collectors.sqlalchemy.private.collector import SQLAlchemyCollector

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
    poolclass=NullPool,
    connect_args={
        "server_settings": {
            "timezone": "UTC",
        },
    },
)

async_session = async_sessionmaker(async_engine, expire_on_commit=False)


class OrmBase(DeclarativeBase):
    pass


class AccountOrm(OrmBase):
    __tablename__ = "accounts"

    id: Mapped[UUID] = mapped_column(primary_key=True, server_default=text("(gen_random_uuid())"))
    name: Mapped[str]
    created: Mapped[datetime] = mapped_column(server_default=func.current_timestamp())
    updated: Mapped[datetime | None] = mapped_column(server_default=None, onupdate=func.current_timestamp())


class TodoItem(OrmBase):
    __tablename__ = "todo_items"

    id: Mapped[UUID] = mapped_column(primary_key=True, server_default=text("(gen_random_uuid())"))
    text: Mapped[str]
    created: Mapped[datetime] = mapped_column(server_default=func.current_timestamp())
    updated: Mapped[datetime | None] = mapped_column(server_default=None, onupdate=func.current_timestamp())


class CollectorTestBase(unittest.IsolatedAsyncioTestCase):
    async def asyncSetUp(self) -> None:
        await super().asyncSetUp()

        async with async_engine.begin() as connection:
            await connection.run_sync(OrmBase.metadata.drop_all)
            await connection.run_sync(OrmBase.metadata.create_all)

        self._write_queue = EphemeralWriteQueue()
        self._collector = SQLAlchemyCollector(write_queue=self._write_queue)
        await self._collector.start(engine=async_engine)

    async def asyncTearDown(self) -> None:
        await super().asyncTearDown()
        CORR_CTX.clear()

    async def test_after_execute_insert(self) -> None:
        assert len(self._write_queue.queue) == 0
        account_name = uuid.uuid4().hex

        async with async_session.begin() as session:
            account = AccountOrm(name=account_name)
            session.add(account)

        assert len(self._write_queue.queue) == 1
        e = self._write_queue.queue[0]
        assert isinstance(e, DatabaseEventPayload)
        assert e.table_name == "accounts"
        assert e.operation == DatabaseOperation.INSERT
        assert e.db_name == db_uri.database
        assert e.parameters is not None
        assert e.parameters["name"] == account_name
        assert "__primary_key" in e.parameters

    async def test_after_execute_update(self) -> None:
        assert len(self._write_queue.queue) == 0
        account_name = uuid.uuid4().hex

        async with async_session.begin() as session:
            account = AccountOrm(name=account_name)
            session.add(account)

        assert len(self._write_queue.queue) == 1
        e0 = self._write_queue.queue[0]
        assert isinstance(e0, DatabaseEventPayload)
        assert e0.parameters is not None

        async with async_session.begin() as session:
            r = await session.get_one(entity=AccountOrm, ident=tuple(e0.parameters["__primary_key"]))
            assert len(self._write_queue.queue) == 2
            e = self._write_queue.queue[1]
            assert isinstance(e, DatabaseEventPayload)
            assert e.table_name == "accounts"
            assert e.operation == DatabaseOperation.SELECT

            new_account_name = uuid.uuid4().hex
            r.name = new_account_name

        assert len(self._write_queue.queue) == 3
        e = self._write_queue.queue[2]
        assert isinstance(e, DatabaseEventPayload)
        assert e.table_name == "accounts"
        assert e.operation == DatabaseOperation.UPDATE
        assert e.db_name == db_uri.database
        assert e.parameters is not None
        assert e.parameters["name"] == new_account_name

    async def test_update_accounts_table_saves_id_to_corr_ctx(self) -> None:
        assert len(self._write_queue.queue) == 0
        account_name = uuid.uuid4().hex

        # setup initial account to update
        async with async_session.begin() as session:
            account = AccountOrm(name=account_name)
            session.add(account)

        assert len(self._write_queue.queue) == 1
        e = self._write_queue.queue[0]
        assert isinstance(e, DatabaseEventPayload)
        assert e.parameters is not None

        async with async_session.begin() as session:
            # fetch row to update
            r = await session.get_one(entity=AccountOrm, ident=account.id)
            assert len(self._write_queue.queue) == 2
            e = self._write_queue.queue[1]
            assert isinstance(e, DatabaseEventPayload)
            assert e.table_name == "accounts"
            assert e.operation == DatabaseOperation.SELECT
            # clear ctx to ensure update sets user_id
            CORR_CTX.clear()

            # do sql update
            new_account_name = uuid.uuid4().hex
            r.name = new_account_name

        assert len(self._write_queue.queue) == 3
        e = self._write_queue.queue[2]
        assert isinstance(e, DatabaseEventPayload)
        assert e.table_name == "accounts"
        assert e.operation == DatabaseOperation.UPDATE
        assert e.db_name == db_uri.database
        assert e.parameters is not None
        assert e.parameters["name"] == new_account_name
        assert CORR_CTX.get("user_id") == str(account.id)
        assert e.context is not None
        assert e.context.get("user_id") == str(account.id)

    async def test_after_execute_insert_account_table(self) -> None:
        assert len(self._write_queue.queue) == 0

        async with async_session.begin() as session:
            account = AccountOrm(name=uuid.uuid4().hex)
            session.add(account)

        assert len(self._write_queue.queue) == 1
        e = self._write_queue.queue[0]

        assert CORR_CTX.get("user_id") == str(account.id)
        assert e.context is not None
        assert e.context.get("user_id") == str(account.id)

    async def test_after_execute_insert_not_account_table(self) -> None:
        assert len(self._write_queue.queue) == 0

        async with async_session.begin() as session:
            orm = TodoItem(text=uuid.uuid4().hex)
            session.add(orm)

        assert len(self._write_queue.queue) == 1
        e = self._write_queue.queue[0]

        assert CORR_CTX.get("user_id") is None
        assert e.context is not None
        assert e.context.get("user_id") is None

    async def test_multi_condition_select_from_account_table(self) -> None:
        assert len(self._write_queue.queue) == 0

        # create an item to query
        account_name = uuid.uuid4().hex
        async with async_session.begin() as session:
            account = AccountOrm(name=account_name)
            session.add(account)

        assert len(self._write_queue.queue) == 1
        # clear ctx to test context writing on SELECT queries
        CORR_CTX.clear()

        # create multi condition where-clause
        lookup = (
            sqlalchemy.select(AccountOrm)
            .where(AccountOrm.id == account.id)
            .where(AccountOrm.name == account_name)
            .limit(1)
        )
        async with async_session.begin() as session:
            result = await session.scalar(lookup)
        assert result is not None

        assert len(self._write_queue.queue) == 2
        e = self._write_queue.queue[1]
        assert isinstance(e, DatabaseEventPayload)
        assert e.table_name == "accounts"
        assert e.operation == DatabaseOperation.SELECT
        assert CORR_CTX.get("user_id") == str(account.id)
        assert e.context is not None
        assert e.context.get("user_id") == str(account.id)

    async def test_single_condition_select_from_account_table(self) -> None:
        assert len(self._write_queue.queue) == 0

        # create an item to query
        account_name = uuid.uuid4().hex
        async with async_session.begin() as session:
            account = AccountOrm(name=account_name)
            session.add(account)

        assert len(self._write_queue.queue) == 1
        # clear ctx to test context writing on SELECT queries
        CORR_CTX.clear()

        # create single condition where-clause
        lookup = sqlalchemy.select(AccountOrm).where(AccountOrm.id == account.id).limit(1)
        async with async_session.begin() as session:
            result = await session.scalar(lookup)
        assert result is not None

        assert len(self._write_queue.queue) == 2
        e = self._write_queue.queue[1]
        assert isinstance(e, DatabaseEventPayload)
        assert e.table_name == "accounts"
        assert e.operation == DatabaseOperation.SELECT
        assert CORR_CTX.get("user_id") == str(account.id)
        assert e.context is not None
        assert e.context.get("user_id") == str(account.id)
