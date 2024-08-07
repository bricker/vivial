from datetime import datetime
from typing import Self, TypedDict, Unpack
from urllib.parse import urlparse
from uuid import UUID

import sqlalchemy.dialects.postgresql
import sqlalchemy.types
from sqlalchemy import Select, func, select, text
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import Mapped, mapped_column

import eave.stdlib.util
from eave.stdlib.core_api.models.team import Team

from .base import Base
from .util import UUID_DEFAULT_EXPR


class TeamOrm(Base):
    __tablename__ = "teams"

    id: Mapped[UUID] = mapped_column(primary_key=True, server_default=UUID_DEFAULT_EXPR)
    name: Mapped[str]
    allowed_origins: Mapped[list[str]] = mapped_column(
        type_=sqlalchemy.dialects.postgresql.ARRAY(
            item_type=sqlalchemy.types.String,
            dimensions=1,
        ),
        server_default=text("'{}'"),
    )
    dashboard_access: Mapped[bool] = mapped_column(server_default=sqlalchemy.sql.false())
    created: Mapped[datetime] = mapped_column(server_default=func.current_timestamp())
    updated: Mapped[datetime | None] = mapped_column(server_default=None, onupdate=func.current_timestamp())

    @classmethod
    async def create(
        cls,
        session: AsyncSession,
        name: str,
        allowed_origins: list[str] | None = None,
    ) -> Self:
        obj = cls(
            name=name,
            allowed_origins=allowed_origins,
        )
        session.add(obj)
        await session.flush()
        return obj

    @property
    def api_model(self) -> Team:
        return Team.from_orm(self)

    class QueryParams(TypedDict):
        team_id: UUID | str

    @classmethod
    def query(cls, **kwargs: Unpack[QueryParams]) -> Select[tuple[Self]]:
        team_id = eave.stdlib.util.ensure_uuid(kwargs["team_id"])
        lookup = select(cls).where(cls.id == team_id)
        return lookup

    @classmethod
    async def one_or_exception(cls, session: AsyncSession, **kwargs: Unpack[QueryParams]) -> Self:
        lookup = cls.query(**kwargs).limit(1)
        result = (await session.scalars(lookup)).one()
        return result

    @classmethod
    async def one_or_none(cls, session: AsyncSession, **kwargs: Unpack[QueryParams]) -> Self | None:
        lookup = cls.query(**kwargs).limit(1)
        result = await session.scalar(lookup)
        return result

    def origin_allowed(self, origin: str) -> bool:
        url = urlparse(url=origin)
        hostname = url.hostname or url.netloc.split(":", maxsplit=1)[0]
        return any(
            self._hostname_matches(hostname=hostname, origin_pattern=pattern) for pattern in self.allowed_origins
        )

    def _hostname_matches(self, hostname: str, origin_pattern: str) -> bool:
        # Remove HTTP(S) scheme prefix and any path. It shouldn't be included in the allowed origins, but it's natural to include it (especially because the Origin header includes it),
        # so we'll just allow it for better UX.
        # origin_pattern = re.sub("^(https?:)?//", "", origin_pattern, count=1, flags=re.IGNORECASE)
        # origin_pattern = re.sub("/.*$", "", origin_pattern, count=1, flags=re.IGNORECASE)

        if origin_pattern == "*":
            # All origins allowed.
            return True

        if origin_pattern.startswith("*."):
            # Wildcard prefix was given.
            # Match the base domain with the END of the hostname, eg:
            #   hostname = dashboard.eave.run
            #   origin_pattern = *.eave.run
            basedomain = origin_pattern.removeprefix("*.")
            return hostname.endswith(basedomain)

        # Otherwise, the hostname must exactly match the origin pattern.
        return hostname == origin_pattern


def bq_dataset_id(id: UUID) -> str:
    return f"team_{id.hex}"
