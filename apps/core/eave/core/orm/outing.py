from datetime import UTC, datetime
from typing import TYPE_CHECKING, Self
from uuid import UUID
from zoneinfo import ZoneInfo

from sqlalchemy import ForeignKey, ForeignKeyConstraint, PrimaryKeyConstraint
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import Mapped, mapped_column, relationship

from eave.core.graphql.types.restaurant import RestaurantSource
from eave.core.orm.account import AccountOrm
from eave.core.orm.survey import SurveyOrm
from eave.core.orm.util.mixins import GetOneByIdMixin, TimedEventMixin
from eave.core.orm.util.user_defined_column_types import ActivitySourceColumnType, RestaurantSourceColumnType
from eave.core.shared.enums import ActivitySource

from .base import Base
from .util.constants import PG_UUID_EXPR, OnDeleteOption

class OutingOrm(Base, GetOneByIdMixin):
    __tablename__ = "outings"
    __table_args__ = (
    )

    id: Mapped[UUID] = mapped_column(primary_key=True, server_default=PG_UUID_EXPR)
    visitor_id: Mapped[UUID] = mapped_column()

    survey_id: Mapped[UUID] = mapped_column(ForeignKey(f"{SurveyOrm.__tablename__}.id", ondelete=OnDeleteOption.CASCADE))
    survey: Mapped[SurveyOrm] = relationship(lazy="selectin")

    account_id: Mapped[UUID | None] = mapped_column(ForeignKey(f"{AccountOrm.__tablename__}.id", ondelete=OnDeleteOption.SET_NULL))
    account: Mapped[AccountOrm] = relationship(lazy="selectin")

    activities: Mapped[list["OutingActivityOrm"]] = relationship(lazy="selectin")
    reservations: Mapped[list["OutingReservationOrm"]] = relationship(lazy="selectin")

    @classmethod
    def build(
        cls,
        *,
        visitor_id: UUID,
        survey_id: UUID,
        account_id: UUID | None = None,
    ) -> "OutingOrm":
        obj = OutingOrm(
            visitor_id=visitor_id,
            account_id=account_id,
            survey_id=survey_id,
        )

        return obj

class OutingActivityOrm(Base, TimedEventMixin):
    """Pivot table between `outings` and activity sources"""

    __tablename__ = "outing_activities"
    __table_args__ = (
        PrimaryKeyConstraint("outing_id", "source_id", name="outing_activity_pivot_pk"),
    )

    outing_id: Mapped[UUID] = mapped_column(ForeignKey(f"{OutingOrm.__tablename__}.id", ondelete=OnDeleteOption.CASCADE))
    source_id: Mapped[str] = mapped_column()
    """ID of activity in remote table"""
    source: Mapped[ActivitySource] = mapped_column(type_=ActivitySourceColumnType())
    """ActivitySource enum value"""
    headcount: Mapped[int] = mapped_column()

    @classmethod
    def build(
        cls,
        *,
        outing_id: UUID,
        source_id: str,
        source: ActivitySource,
        start_time_utc: datetime,
        timezone: ZoneInfo,
        headcount: int,
    ) -> "OutingActivityOrm":
        obj = OutingActivityOrm(
            outing_id=outing_id,
            source_id=source_id,
            source=source,
            start_time_utc=start_time_utc.astimezone(UTC),
            timezone=timezone,
            headcount=headcount,
        )

        return obj

    @classmethod
    async def get_one_by_outing_id(cls, session: AsyncSession, outing_id: UUID) -> Self:
        lookup = cls.select().where(cls.outing_id == outing_id)
        result = (await session.scalars(lookup)).one()
        return result


class OutingReservationOrm(Base, TimedEventMixin):
    """Pivot table between `outings` and reservation sources"""

    __tablename__ = "outing_reservations"
    __table_args__ = (
        PrimaryKeyConstraint("outing_id", "source_id", name="outing_reservation_pivot_pk"),
    )

    outing_id: Mapped[UUID] = mapped_column(ForeignKey(f"{OutingOrm.__tablename__}.id", ondelete=OnDeleteOption.CASCADE))
    source_id: Mapped[str] = mapped_column()
    """ID of reservation in remote table"""
    source: Mapped[RestaurantSource] = mapped_column(type_=RestaurantSourceColumnType())
    """RestaurantSource enum value"""
    headcount: Mapped[int] = mapped_column()

    @classmethod
    def build(
        cls,
        *,
        outing_id: UUID,
        source_id: str,
        source: RestaurantSource,
        start_time_utc: datetime,
        timezone: ZoneInfo,
        headcount: int,
    ) -> "OutingReservationOrm":
        obj = OutingReservationOrm(
            outing_id=outing_id,
            source_id=source_id,
            source=source,
            start_time_utc=start_time_utc.astimezone(UTC),
            timezone=timezone,
            headcount=headcount,
        )

        return obj

    @classmethod
    async def get_one_by_outing_id(cls, session: AsyncSession, outing_id: UUID) -> Self:
        lookup = cls.select().where(cls.outing_id == outing_id)
        result = (await session.scalars(lookup)).one()
        return result
