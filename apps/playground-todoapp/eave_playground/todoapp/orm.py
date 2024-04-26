import os
from datetime import datetime
from typing import Any
from uuid import UUID

from eave.stdlib.typing import JsonValue
import sqlalchemy
from sqlalchemy import ForeignKey, NullPool, func, text
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column

db_uri = sqlalchemy.engine.url.URL.create(
    drivername="postgresql+asyncpg",
    host=os.getenv("TODOAPP_DB_HOST", "localhost"),
    port=int(os.getenv("TODOAPP_DB_PORT", "5432")),
    username=os.getenv("TODOAPP_DB_USER"),
    password=os.getenv("TODOAPP_DB_PASS"),
    database=os.getenv("TODOAPP_DB_DATABASE", "playground-todoapp"),
)

async_engine = create_async_engine(
    db_uri,
    echo=False,
    connect_args={
        "server_settings": {
            "timezone": "UTC",
            "application_name": "playground-todoapp",
        },
    },
)

async_session = async_sessionmaker(async_engine, expire_on_commit=False)


class BaseOrm(DeclarativeBase):
    pass


class UserOrm(BaseOrm):
    __tablename__ = "users"

    id: Mapped[UUID] = mapped_column(primary_key=True, server_default=text("(gen_random_uuid())"))
    username: Mapped[str] = mapped_column()
    visitor_id: Mapped[str | None] = mapped_column()
    utm_params: Mapped[str | None] = mapped_column()
    created: Mapped[datetime] = mapped_column(server_default=func.current_timestamp())
    updated: Mapped[datetime | None] = mapped_column(server_default=None, onupdate=func.current_timestamp())


class TodoListItemOrm(BaseOrm):
    __tablename__ = "todo_list_items"

    id: Mapped[UUID] = mapped_column(primary_key=True, server_default=text("(gen_random_uuid())"))
    user_id: Mapped[UUID] = mapped_column(ForeignKey("users.id"))
    text: Mapped[str] = mapped_column()
    created: Mapped[datetime] = mapped_column(server_default=func.current_timestamp())
    updated: Mapped[datetime | None] = mapped_column(server_default=None, onupdate=func.current_timestamp())

    def render(self) -> dict[str, JsonValue]:
        return {
            "id": self.id.hex,
            "user_id": self.user_id.hex,
            "text": self.text,
            "created": self.created.isoformat(),
            "updated": self.updated.isoformat() if self.updated else None,
        }
