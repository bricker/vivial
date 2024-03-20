from dataclasses import dataclass
import uuid
from datetime import datetime
from typing import NotRequired, Optional, Self, Tuple, TypedDict, Unpack
from uuid import UUID

from sqlalchemy import Select, func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import Mapped, mapped_column

from eave.stdlib.core_api.models.metabase_instance import MetabaseInstance

from .base import Base
from .util import UUID_DEFAULT_EXPR, make_team_fk, make_team_composite_pk


class MetabaseInstanceOrm(Base):
    __tablename__ = "metabase_instances"
    __table_args__ = (
        make_team_composite_pk(table_name="metabase_instances"),
        make_team_fk(),
    )

    team_id: Mapped[UUID] = mapped_column()
    id: Mapped[UUID] = mapped_column(server_default=UUID_DEFAULT_EXPR)
    jwt_signing_key: Mapped[Optional[str]] = mapped_column(server_default=None)
    route_id: Mapped[Optional[uuid.UUID]] = mapped_column(server_default=None)
    created: Mapped[datetime] = mapped_column(server_default=func.current_timestamp())
    updated: Mapped[Optional[datetime]] = mapped_column(server_default=None, onupdate=func.current_timestamp())

    @classmethod
    async def create(
        cls,
        session: AsyncSession,
        team_id: Optional[uuid.UUID],
    ) -> Self:
        obj = cls(
            team_id=team_id,
        )
        session.add(obj)
        await session.flush()
        return obj

    class UpdateParameters(TypedDict):
        jwt_signing_key: NotRequired[str]
        route_id: NotRequired[uuid.UUID]

    def update(
        self,
        session: AsyncSession,
        **kwargs: Unpack[UpdateParameters],
    ) -> Self:
        """session parameter required (although unused) to indicate this should only be called w/in a db session"""
        if jwt_signing_key := kwargs.get("jwt_signing_key"):
            self.jwt_signing_key = jwt_signing_key

        if route_id := kwargs.get("route_id"):
            self.route_id = route_id
        return self

    @dataclass
    class QueryParams:
        team_id: Optional[uuid.UUID] = None
        id: Optional[uuid.UUID] = None

        def validate_or_exception(self):
            assert self.team_id or self.id, "At least one query parameter must be given"

    @classmethod
    def _build_select(cls, params: QueryParams) -> Select[Tuple[Self]]:
        params.validate_or_exception()

        lookup = select(cls)

        if params.team_id:
            lookup = lookup.where(cls.team_id == params.team_id)

        if params.id:
            lookup = lookup.where(cls.id == params.id)

        assert lookup.whereclause is not None, "Invalid parameters"
        return lookup

    @classmethod
    async def query(cls, session: AsyncSession, params: QueryParams) -> Self | None:
        lookup = cls._build_select(params=params).limit(1)
        result = await session.scalar(lookup)
        return result

    @classmethod
    async def one_or_none(cls, session: AsyncSession, team_id: UUID) -> Self | None:
        lookup = cls._build_select(params=cls.QueryParams(team_id=team_id)).limit(1)
        result = await session.scalar(lookup)
        return result

    @classmethod
    async def one_or_exception(cls, session: AsyncSession, team_id: UUID) -> Self:
        lookup = cls._build_select(params=cls.QueryParams(team_id=team_id)).limit(1)
        result = (await session.scalars(lookup)).one()
        return result

    @property
    def api_model(self) -> MetabaseInstance:
        return MetabaseInstance.from_orm(self)

    def validate_hosting_data(self):
        assert self.jwt_signing_key is not None, "Metabase instance doesn't have a signing key"
        assert self.route_id is not None, "Metabase instance doesn't have hosted route ID"
