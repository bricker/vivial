from datetime import datetime
import os
from typing import Any
from uuid import UUID
from sqlalchemy import ForeignKey, NullPool, func, text
import sqlalchemy
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine
from sqlalchemy.ext.asyncio.session import AsyncSession
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship


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
    # poolclass=NullPoll is a hack only acceptable for this playground app.
    # Long story short: The Flask development server isn't perfectly compatible with SQLAlchemy's asyncio extension, and this works around that.
    poolclass=NullPool,
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
    visitor_id: Mapped[UUID | None] = mapped_column()
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

    def render(self) -> dict[str, Any]:
        return {
            "id": self.id,
            "user_id": self.user_id,
            "text": self.text,
            "created": self.created,
            "updated": self.updated,
        }
