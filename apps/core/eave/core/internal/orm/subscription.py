from datetime import datetime
from typing import Optional, Self, Tuple
from uuid import UUID

import eave.stdlib.core_api.enums
import eave.stdlib.core_api.models as eave_models
from sqlalchemy import Index, Select, func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import Mapped, mapped_column

from . import (
    UUID_DEFAULT_EXPR,
    Base,
    make_team_composite_fk,
    make_team_composite_pk,
    make_team_fk,
)
from .document_reference import DocumentReferenceOrm


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
    source_platform: Mapped[eave.stdlib.core_api.enums.SubscriptionSourcePlatform] = mapped_column()
    source_event: Mapped[eave.stdlib.core_api.enums.SubscriptionSourceEvent] = mapped_column()
    source_id: Mapped[str] = mapped_column()
    document_reference_id: Mapped[Optional[UUID]] = mapped_column()
    created: Mapped[datetime] = mapped_column(server_default=func.current_timestamp())
    updated: Mapped[Optional[datetime]] = mapped_column(server_default=None, onupdate=func.current_timestamp())

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
    def source(self) -> eave_models.SubscriptionSource:
        return eave_models.SubscriptionSource(
            platform=self.source_platform,
            event=self.source_event,
            id=self.source_id,
        )

    @source.setter
    def source(self, source: eave_models.SubscriptionSource) -> None:
        self.source_platform = source.platform
        self.source_event = source.event
        self.source_id = source.id

    @classmethod
    async def one_or_none(
        cls, session: AsyncSession, team_id: UUID, source: eave_models.SubscriptionSource
    ) -> Optional[Self]:
        lookup = cls._select_one(team_id=team_id, source=source)
        subscription = await session.scalar(lookup)
        return subscription

    @classmethod
    async def one_or_exception(
        cls, session: AsyncSession, team_id: UUID, source: eave_models.SubscriptionSource
    ) -> Self:
        lookup = cls._select_one(team_id=team_id, source=source)
        subscription = (await session.scalars(lookup)).one()
        return subscription

    @classmethod
    def _select_one(cls, team_id: UUID, source: eave_models.SubscriptionSource) -> Select[Tuple[Self]]:
        lookup = (
            select(cls)
            .where(cls.team_id == team_id)
            .where(cls.source_platform == source.platform)
            .where(cls.source_event == source.event)
            .where(cls.source_id == source.id)
            .limit(1)
        )
        return lookup
