from datetime import datetime
from typing import NotRequired, Optional, Required, Self, Sequence, Tuple, TypedDict, Unpack
from uuid import UUID

from sqlalchemy import Index, Select, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import Mapped, mapped_column
from eave.stdlib.core_api.models.subscriptions import (
    SubscriptionSource,
    SubscriptionSourceEvent,
    SubscriptionSourcePlatform,
)
from eave.stdlib.core_api.models.subscriptions import (
    Subscription,
)

from eave.stdlib.util import ensure_uuid

from .base import Base
from .document_reference import DocumentReferenceOrm
from .util import UUID_DEFAULT_EXPR, make_team_composite_fk, make_team_composite_pk, make_team_fk, current_timestamp_utc


class SubscriptionOrm(Base):
    __tablename__ = "subscriptions"
    __table_args__ = (
        make_team_composite_pk(),
        make_team_fk(),
        make_team_composite_fk("document_reference_id", "document_references"),
        Index(
            "source_key",
            "team_id",
            "source_platform",
            "source_event",
            "source_id",
            unique=True,
        ),
    )

    team_id: Mapped[UUID] = mapped_column()
    id: Mapped[UUID] = mapped_column(server_default=UUID_DEFAULT_EXPR)
    source_platform: Mapped[SubscriptionSourcePlatform] = mapped_column()
    source_event: Mapped[SubscriptionSourceEvent] = mapped_column()
    source_id: Mapped[str] = mapped_column()
    document_reference_id: Mapped[Optional[UUID]] = mapped_column()
    created: Mapped[datetime] = mapped_column(server_default=current_timestamp_utc())
    updated: Mapped[Optional[datetime]] = mapped_column(server_default=None, onupdate=current_timestamp_utc())

    @property
    def api_model(self) -> Subscription:
        return Subscription.from_orm(self)

    async def get_document_reference(self, session: AsyncSession) -> Optional[DocumentReferenceOrm]:
        if self.document_reference_id is None:
            return None

        result = await DocumentReferenceOrm.one_or_exception(
            team_id=self.team_id,
            id=self.document_reference_id,
            session=session,
        )
        return result

    @property
    def source(self) -> SubscriptionSource:
        return SubscriptionSource(
            platform=self.source_platform,
            event=self.source_event,
            id=self.source_id,
        )

    @source.setter
    def source(self, source: SubscriptionSource) -> None:
        self.source_platform = source.platform
        self.source_event = source.event
        self.source_id = source.id

    @classmethod
    async def create(
        cls,
        session: AsyncSession,
        team_id: UUID,
        source: SubscriptionSource,
        document_reference_id: Optional[UUID] = None,
    ) -> Self:
        obj = cls(
            team_id=team_id,
            source_platform=source.platform,
            source_event=source.event,
            source_id=source.id,
            document_reference_id=document_reference_id,
        )
        session.add(obj)
        await session.flush()
        return obj

    class QueryParams(TypedDict):
        team_id: Required[UUID | str]
        id: NotRequired[UUID | str]
        source: NotRequired[SubscriptionSource]
        document_reference_id: NotRequired[UUID | str]

    @classmethod
    def _build_query(cls, **kwargs: Unpack[QueryParams]) -> Select[Tuple[Self]]:
        lookup = select(cls)
        team_id = kwargs.get("team_id")
        lookup = lookup.where(cls.team_id == ensure_uuid(team_id))

        if id := kwargs.get("id"):
            id = ensure_uuid(id)
            lookup = lookup.where(cls.id == id)

        if document_reference_id := kwargs.get("document_reference_id"):
            document_reference_id = ensure_uuid(document_reference_id)
            lookup = lookup.where(cls.document_reference_id == document_reference_id)

        if source := kwargs.get("source"):
            lookup = (
                lookup.where(cls.source_platform == source.platform)
                .where(cls.source_event == source.event)
                .where(cls.source_id == source.id)
            )

        assert lookup.whereclause is not None, "Invalid parameters"
        return lookup

    @classmethod
    async def query(cls, session: AsyncSession, **kwargs: Unpack[QueryParams]) -> Sequence[Self]:
        lookup = cls._build_query(**kwargs)
        result = (await session.scalars(lookup)).all()
        return result

    @classmethod
    async def one_or_none(cls, session: AsyncSession, **kwargs: Unpack[QueryParams]) -> Optional[Self]:
        lookup = cls._build_query(**kwargs).limit(1)
        result = (await session.scalars(lookup)).one_or_none()
        return result

    @classmethod
    async def one_or_exception(cls, session: AsyncSession, **kwargs: Unpack[QueryParams]) -> Self:
        lookup = cls._build_query(**kwargs).limit(1)
        result = (await session.scalars(lookup)).one()
        return result
