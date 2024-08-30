import os
from typing import cast
import unittest.mock
import uuid
from datetime import datetime
from uuid import UUID

import sqlalchemy
from sqlalchemy import NullPool, PrimaryKeyConstraint, func, text
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column

from eave.collectors.core.config import EaveCredentials
from eave.collectors.core.correlation_context import CORR_CTX
from eave.collectors.core.correlation_context.base import (
    CorrelationContextAttr,
    corr_ctx_symmetric_encryption_key,
)
from eave.collectors.core.datastructures import DatabaseEventPayload, DatabaseOperation, EventPayload
from eave.collectors.core.json import JsonScalar
from eave.collectors.core.test_util import EphemeralWriteQueue
from eave.collectors.sqlalchemy.private.collector import SQLAlchemyCollector

db_uri = sqlalchemy.engine.url.URL.create(
    drivername="postgresql+asyncpg",
    host=os.getenv("EAVE_DB_HOST", "localhost"),
    port=int(os.getenv("EAVE_DB_PORT", "5432")),
    username=os.getenv("EAVE_DB_USER", None),
    password=os.getenv("EAVE_DB_PASS", None),
    database="eave-sqlalchemy-tests",
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

    # un-official foreign keys
    snake_team_id: Mapped[UUID | None] = mapped_column(server_default=None)
    camelTeamId: Mapped[UUID | None] = mapped_column(server_default=None)  # noqa: N815


class UserComposite(OrmBase):
    __tablename__ = "users"
    __table_args__ = (
        PrimaryKeyConstraint(
            "secondary_id",
            "id",
            name="pk_secondary_id_id",
        ),
    )
    # composite pk
    id: Mapped[UUID] = mapped_column(primary_key=True, server_default=text("(gen_random_uuid())"))
    secondary_id: Mapped[UUID] = mapped_column(primary_key=True, server_default=text("(gen_random_uuid())"))
    created: Mapped[datetime] = mapped_column(server_default=func.current_timestamp())
    updated: Mapped[datetime | None] = mapped_column(server_default=None, onupdate=func.current_timestamp())


class TodoItem(OrmBase):
    __tablename__ = "todo_items"

    id: Mapped[UUID] = mapped_column(primary_key=True, server_default=text("(gen_random_uuid())"))
    text: Mapped[str]
    created: Mapped[datetime] = mapped_column(server_default=func.current_timestamp())
    updated: Mapped[datetime | None] = mapped_column(server_default=None, onupdate=func.current_timestamp())

    # un-official foreign key
    checklist_id: Mapped[UUID | None] = mapped_column(server_default=None)


class Team(OrmBase):
    __tablename__ = "test_teams"

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

        self._write_queue = EphemeralWriteQueue()
        self._collector = SQLAlchemyCollector(write_queue=self._write_queue)
        self._collector.start(engine=async_engine)

    def _get_encrypted_attr(self, attr_name: str, corr_ctx: dict[str, JsonScalar]) -> CorrelationContextAttr | None:
        creds = EaveCredentials.from_env()
        assert creds is not None

        encryption_key = corr_ctx_symmetric_encryption_key(creds.combined)

        encrypted_attrs = [
            CorrelationContextAttr.from_encrypted(decryption_key=encryption_key, encrypted_value=str(value))
            for _, value in corr_ctx.items()
        ]

        decrypted_attr = next((attr for attr in encrypted_attrs if attr and attr.key == attr_name), None)
        return decrypted_attr

    def _encrypted_attr_was_set(
        self, attr_name: str, event_corr_ctx: dict[str, JsonScalar] | None, expected_value: str | None = None
    ) -> bool:
        assert event_corr_ctx is not None
        storage = CORR_CTX.get_storage()
        assert storage is not None

        event_corr_ctx_attr = self._get_encrypted_attr(attr_name, event_corr_ctx)
        global_corr_ctx_attr = self._get_encrypted_attr(attr_name, storage.updated)

        if event_corr_ctx_attr is None or global_corr_ctx_attr is None:
            return False

        if (
            expected_value is not None
            and event_corr_ctx_attr.value != expected_value
            or global_corr_ctx_attr.value != expected_value
        ):
            return False

        return True

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
        assert e.statement_values is not None
        assert e.statement_values["name"] == account_name
        assert "__primary_keys" in e.statement_values

    async def test_after_execute_update(self) -> None:
        assert len(self._write_queue.queue) == 0
        account_name = uuid.uuid4().hex

        async with async_session.begin() as session:
            account = AccountOrm(name=account_name)
            session.add(account)

        assert len(self._write_queue.queue) == 1
        e0 = self._write_queue.queue[0]
        assert isinstance(e0, DatabaseEventPayload)
        assert e0.statement_values is not None

        async with async_session.begin() as session:
            # (("id", "1234567.."),)
            pk = e0.statement_values["__primary_keys"][0][1]
            r = await session.get_one(entity=AccountOrm, ident=(pk,))
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
        assert e.statement_values is not None
        assert e.statement_values["name"] == new_account_name

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
        assert e.statement_values is not None

        async with async_session.begin() as session:
            # clear ctx to ensure update was the op to set account_id
            CORR_CTX.clear()

            # do sql update
            new_account_name = uuid.uuid4().hex
            account.name = new_account_name
            session.add(account)

        assert len(self._write_queue.queue) == 2
        e = self._write_queue.queue[1]
        assert isinstance(e, DatabaseEventPayload)
        assert e.table_name == "accounts"
        assert e.operation == DatabaseOperation.UPDATE
        assert e.db_name == db_uri.database
        assert e.statement_values is not None
        assert e.statement_values["name"] == new_account_name
        assert self._encrypted_attr_was_set(
            attr_name="account_id", expected_value=str(account.id), event_corr_ctx=e.corr_ctx
        )

    async def test_after_execute_insert_account_table(self) -> None:
        assert len(self._write_queue.queue) == 0

        async with async_session.begin() as session:
            account = AccountOrm(name=uuid.uuid4().hex)
            session.add(account)

        assert len(self._write_queue.queue) == 1
        e = cast(EventPayload, self._write_queue.queue[0])
        assert self._encrypted_attr_was_set(
            attr_name="account_id", expected_value=str(account.id), event_corr_ctx=e.corr_ctx
        )

    async def test_after_execute_insert_not_account_table(self) -> None:
        assert len(self._write_queue.queue) == 0

        async with async_session.begin() as session:
            orm = TodoItem(text=uuid.uuid4().hex)
            session.add(orm)

        assert len(self._write_queue.queue) == 1
        e = cast(EventPayload, self._write_queue.queue[0])
        assert not self._encrypted_attr_was_set(attr_name="account_id", event_corr_ctx=e.corr_ctx)

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
        assert self._encrypted_attr_was_set(
            attr_name="account_id", expected_value=str(account.id), event_corr_ctx=e.corr_ctx
        )

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
        assert self._encrypted_attr_was_set(
            attr_name="account_id", expected_value=str(account.id), event_corr_ctx=e.corr_ctx
        )

    async def test_account_foreign_keys_captured_in_context_after_insert(self):
        assert len(self._write_queue.queue) == 0

        # insert "fk" model
        async with async_session.begin() as session:
            team = Team(name=uuid.uuid4().hex)
            session.add(team)

        assert len(self._write_queue.queue) == 1
        e = cast(EventPayload, self._write_queue.queue[0])
        # no context data should be written yet
        assert e.corr_ctx == {}

        # insert account w/ foreign keys
        async with async_session.begin() as session:
            account = AccountOrm(name=uuid.uuid4().hex, snake_team_id=team.id, camelTeamId=team.id)
            session.add(account)

        assert len(self._write_queue.queue) == 2
        e = self._write_queue.queue[1]

        # pk and fk values should be present in contexts
        assert isinstance(e, DatabaseEventPayload)
        assert e.table_name == "accounts"
        assert e.operation == DatabaseOperation.INSERT
        assert self._encrypted_attr_was_set("account_id", expected_value=str(account.id), event_corr_ctx=e.corr_ctx)
        assert self._encrypted_attr_was_set("snake_team_id", expected_value=str(team.id), event_corr_ctx=e.corr_ctx)
        assert self._encrypted_attr_was_set("camelTeamId", expected_value=str(team.id), event_corr_ctx=e.corr_ctx)

    async def test_account_foreign_keys_captured_in_context_after_update(self):
        assert len(self._write_queue.queue) == 0

        # insert "fk" model
        async with async_session.begin() as session:
            team = Team(name=uuid.uuid4().hex)
            session.add(team)
        assert len(self._write_queue.queue) == 1

        # insert account to update
        async with async_session.begin() as session:
            account = AccountOrm(name=uuid.uuid4().hex)
            session.add(account)
        assert len(self._write_queue.queue) == 2
        # clear for update assertions
        CORR_CTX.clear()

        # update the account
        async with async_session.begin() as session:
            account.snake_team_id = team.id
            account.camelTeamId = team.id
            session.add(account)

        # pk and fk values should be present in contexts
        assert len(self._write_queue.queue) == 3
        e = self._write_queue.queue[2]
        assert isinstance(e, DatabaseEventPayload)
        assert e.table_name == "accounts"
        assert e.operation == DatabaseOperation.UPDATE
        assert self._encrypted_attr_was_set("account_id", expected_value=str(account.id), event_corr_ctx=e.corr_ctx)
        assert self._encrypted_attr_was_set("snake_team_id", expected_value=str(team.id), event_corr_ctx=e.corr_ctx)
        assert self._encrypted_attr_was_set("camelTeamId", expected_value=str(team.id), event_corr_ctx=e.corr_ctx)

    async def test_account_foreign_keys_captured_in_context_after_select(self):
        assert len(self._write_queue.queue) == 0

        # create an item to query
        async with async_session.begin() as session:
            team = Team(name=uuid.uuid4().hex)
            session.add(team)

        async with async_session.begin() as session:
            account = AccountOrm(name=uuid.uuid4().hex, snake_team_id=team.id, camelTeamId=team.id)
            session.add(account)

        assert len(self._write_queue.queue) == 2
        # clear ctx to test context writing on SELECT queries
        CORR_CTX.clear()

        # create SELECT lookup using pk and fk equalities
        lookup = (
            sqlalchemy.select(AccountOrm)
            .where(AccountOrm.id == account.id)
            .where(AccountOrm.snake_team_id == team.id)
            .where(AccountOrm.camelTeamId == team.id)
            .limit(1)
        )
        async with async_session.begin() as session:
            result = await session.scalar(lookup)
        assert result is not None

        # select event should save pk and fk data in context
        assert len(self._write_queue.queue) == 3
        e = self._write_queue.queue[2]
        assert isinstance(e, DatabaseEventPayload)
        assert e.table_name == "accounts"
        assert e.operation == DatabaseOperation.SELECT
        assert self._encrypted_attr_was_set("account_id", expected_value=str(account.id), event_corr_ctx=e.corr_ctx)
        assert self._encrypted_attr_was_set("snake_team_id", expected_value=str(team.id), event_corr_ctx=e.corr_ctx)
        assert self._encrypted_attr_was_set("camelTeamId", expected_value=str(team.id), event_corr_ctx=e.corr_ctx)

    async def test_non_eq_binary_comparisons_in_where_clause_stripped_from_considered_values(self):
        assert len(self._write_queue.queue) == 0

        # create an item to query
        async with async_session.begin() as session:
            team = Team(name=uuid.uuid4().hex)
            session.add(team)

        async with async_session.begin() as session:
            account = AccountOrm(name=uuid.uuid4().hex, snake_team_id=team.id, camelTeamId=team.id)
            session.add(account)

        assert len(self._write_queue.queue) == 2
        # clear ctx to test context writing on SELECT queries
        CORR_CTX.clear()

        # create SELECT lookup comparing a pk/fk with non-equal operator
        max_uuid = uuid.UUID("ffffffff-ffff-4fff-bfff-ffffffffffff")
        lookup = (
            sqlalchemy.select(AccountOrm)
            .where(AccountOrm.id == account.id)
            .where(AccountOrm.snake_team_id == team.id)
            .where(AccountOrm.camelTeamId < max_uuid)
            .limit(1)
        )
        async with async_session.begin() as session:
            result = await session.scalar(lookup)
        assert result is not None

        # select event should not save pk and fk data that
        # was compared with non-eq operator
        assert len(self._write_queue.queue) == 3
        e = self._write_queue.queue[2]
        assert isinstance(e, DatabaseEventPayload)
        assert e.table_name == "accounts"
        assert e.operation == DatabaseOperation.SELECT
        assert self._encrypted_attr_was_set("account_id", expected_value=str(account.id), event_corr_ctx=e.corr_ctx)
        assert self._encrypted_attr_was_set("snake_team_id", expected_value=str(team.id), event_corr_ctx=e.corr_ctx)
        assert not self._encrypted_attr_was_set("camelTeamId", expected_value=str(team.id), event_corr_ctx=e.corr_ctx)

    async def test_composite_pk_order_preserved_in_atom(self):
        assert len(self._write_queue.queue) == 0

        # insert user table w/ composite pk
        async with async_session.begin() as session:
            user = UserComposite()
            session.add(user)

        assert len(self._write_queue.queue) == 1
        e = self._write_queue.queue[0]

        # pk values should both be present in contexts
        assert isinstance(e, DatabaseEventPayload)
        assert e.table_name == "users"
        assert e.operation == DatabaseOperation.INSERT
        assert self._encrypted_attr_was_set("account_id", expected_value=str(user.id), event_corr_ctx=e.corr_ctx)
        assert self._encrypted_attr_was_set(
            "secondary_id", expected_value=str(user.secondary_id), event_corr_ctx=e.corr_ctx
        )

        # __primary_keys order should match table composite pk order
        assert e.statement_values is not None
        assert "__primary_keys" in e.statement_values
        assert e.statement_values["__primary_keys"] == (("secondary_id", str(user.secondary_id)), ("id", str(user.id)))

    async def test_fk_on_non_accounts_table_is_not_added_to_context(self):
        assert len(self._write_queue.queue) == 0

        # insert non account table row that has a fk
        async with async_session.begin() as session:
            item = TodoItem(
                text=uuid.uuid4().hex,
                checklist_id=uuid.uuid4(),
            )
            session.add(item)

        assert len(self._write_queue.queue) == 1
        e = self._write_queue.queue[0]

        # context should be empty, even though row has fk, since it's a non-account table
        assert isinstance(e, DatabaseEventPayload)
        assert e.table_name == "todo_items"
        assert e.operation == DatabaseOperation.INSERT
        assert e.corr_ctx == {}

    # TODO: test inserting multiple records at once w/ one statment. how does code handle that?
