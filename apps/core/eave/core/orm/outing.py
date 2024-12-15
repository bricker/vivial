from datetime import UTC, datetime
from uuid import UUID
from zoneinfo import ZoneInfo

from sqlalchemy import ForeignKey, PrimaryKeyConstraint
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
    __table_args__ = ()

    id: Mapped[UUID] = mapped_column(primary_key=True, server_default=PG_UUID_EXPR)
    visitor_id: Mapped[str | None] = mapped_column()

    survey_id: Mapped[UUID] = mapped_column(
        ForeignKey(f"{SurveyOrm.__tablename__}.id", ondelete=OnDeleteOption.CASCADE.value)
    )
    survey: Mapped[SurveyOrm] = relationship(lazy="selectin")

    account_id: Mapped[UUID | None] = mapped_column(
        ForeignKey(f"{AccountOrm.__tablename__}.id", ondelete=OnDeleteOption.SET_NULL.value)
    )
    account: Mapped[AccountOrm | None] = relationship(lazy="selectin")

    activities: Mapped[list["OutingActivityOrm"]] = relationship(lazy="selectin", back_populates="outing")
    reservations: Mapped[list["OutingReservationOrm"]] = relationship(lazy="selectin", back_populates="outing")

    def __init__(
        self,
        session: AsyncSession | None,
        *,
        visitor_id: str | None,
        survey: SurveyOrm,
        account: AccountOrm | None,
    ) -> None:
        self.visitor_id = visitor_id
        self.account = account
        self.survey = survey

        if session:
            session.add(self)


class OutingActivityOrm(Base, TimedEventMixin):
    """Pivot table between `outings` and activity sources"""

    __tablename__ = "outing_activities"
    __table_args__ = (PrimaryKeyConstraint("outing_id", "source_id", name="outing_activity_pivot_pk"),)

    id: Mapped[UUID] = mapped_column(server_default=PG_UUID_EXPR, unique=True)
    outing_id: Mapped[UUID] = mapped_column(
        ForeignKey(f"{OutingOrm.__tablename__}.id", ondelete=OnDeleteOption.CASCADE.value)
    )
    outing: Mapped[OutingOrm] = relationship(lazy="selectin", back_populates="activities")

    source_id: Mapped[str] = mapped_column()
    """ID of activity in remote table"""
    source: Mapped[ActivitySource] = mapped_column(type_=ActivitySourceColumnType())
    """ActivitySource enum value"""
    headcount: Mapped[int] = mapped_column()

    def __init__(
        self,
        session: AsyncSession | None,
        *,
        outing: OutingOrm,
        source_id: str,
        source: ActivitySource,
        start_time_utc: datetime,
        timezone: ZoneInfo,
        headcount: int,
    ) -> None:
        self.outing = outing
        self.source_id = source_id
        self.source = source
        self.start_time_utc = start_time_utc.astimezone(UTC)
        self.timezone = timezone
        self.headcount = headcount

        if session:
            session.add(self)


class OutingReservationOrm(Base, TimedEventMixin):
    """Pivot table between `outings` and reservation sources"""

    __tablename__ = "outing_reservations"
    __table_args__ = (PrimaryKeyConstraint("outing_id", "source_id", name="outing_reservation_pivot_pk"),)

    id: Mapped[UUID] = mapped_column(server_default=PG_UUID_EXPR, unique=True)
    outing_id: Mapped[UUID] = mapped_column(
        ForeignKey(f"{OutingOrm.__tablename__}.id", ondelete=OnDeleteOption.CASCADE.value)
    )
    outing: Mapped[OutingOrm] = relationship(lazy="selectin", back_populates="reservations")

    source_id: Mapped[str] = mapped_column()
    """ID of reservation in remote table"""
    source: Mapped[RestaurantSource] = mapped_column(type_=RestaurantSourceColumnType())
    """RestaurantSource enum value"""
    headcount: Mapped[int] = mapped_column()

    def __init__(
        self,
        session: AsyncSession | None,
        *,
        outing: OutingOrm,
        source_id: str,
        source: RestaurantSource,
        start_time_utc: datetime,
        timezone: ZoneInfo,
        headcount: int,
    ) -> None:
        self.outing = outing
        self.source_id = source_id
        self.source = source
        self.start_time_utc = start_time_utc.astimezone(UTC)
        self.timezone = timezone
        self.headcount = headcount

        if session:
            session.add(self)
