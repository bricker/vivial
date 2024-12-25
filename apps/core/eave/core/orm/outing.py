from datetime import UTC, datetime
from uuid import UUID
from zoneinfo import ZoneInfo

from sqlalchemy import ForeignKey
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import Mapped, mapped_column, relationship

from eave.core.graphql.types.restaurant import RestaurantSource
from eave.core.orm.account import AccountOrm
from eave.core.orm.survey import SurveyOrm
from eave.core.orm.util.mixins import GetOneByIdMixin, TimedEventMixin
from eave.core.orm.util.user_defined_column_types import ActivitySourceColumnType, RestaurantSourceColumnType
from eave.core.shared.enums import ActivitySource

from .base import Base
from .util.constants import CASCADE_ALL_DELETE_ORPHAN, PG_UUID_EXPR, OnDeleteOption


class OutingOrm(Base, GetOneByIdMixin):
    __tablename__ = "outings"

    id: Mapped[UUID] = mapped_column(primary_key=True, server_default=PG_UUID_EXPR)
    visitor_id: Mapped[str | None] = mapped_column()

    survey_id: Mapped[UUID | None] = mapped_column(
        ForeignKey(f"{SurveyOrm.__tablename__}.id", ondelete=OnDeleteOption.SET_NULL.value)
    )
    survey: Mapped[SurveyOrm | None] = relationship(lazy="selectin")

    account_id: Mapped[UUID | None] = mapped_column(
        ForeignKey(f"{AccountOrm.__tablename__}.id", ondelete=OnDeleteOption.SET_NULL.value)
    )
    account: Mapped[AccountOrm | None] = relationship(lazy="selectin")

    activities: Mapped[list["OutingActivityOrm"]] = relationship(
        lazy="selectin", back_populates="outing", cascade=CASCADE_ALL_DELETE_ORPHAN
    )
    reservations: Mapped[list["OutingReservationOrm"]] = relationship(
        lazy="selectin", back_populates="outing", cascade=CASCADE_ALL_DELETE_ORPHAN
    )

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

    @property
    def timezone(self) -> ZoneInfo:
        if len(self.activities) > 0:
            return self.activities[0].timezone
        elif len(self.reservations) > 0:
            return self.reservations[0].timezone
        else:
            raise ValueError("Invalid Outing: no activities or reservations")

    @property
    def start_time_utc(self) -> datetime:
        candidates: list[datetime] = []
        candidates.extend(a.start_time_utc for a in self.activities)
        candidates.extend(r.start_time_utc for r in self.reservations)

        if len(candidates) == 0:
            raise ValueError("Invalid Outing: no activities or reservations")

        return min(candidates)

    @property
    def start_time_local(self) -> datetime:
        candidates: list[datetime] = []
        candidates.extend(a.start_time_local for a in self.activities)
        candidates.extend(r.start_time_local for r in self.reservations)

        if len(candidates) == 0:
            raise ValueError("Invalid Outing: no activities or reservations")

        return min(candidates)

    @property
    def headcount(self) -> int:
        candidates: list[int] = []
        candidates.extend(a.headcount for a in self.activities)
        candidates.extend(r.headcount for r in self.reservations)

        if len(candidates) == 0:
            raise ValueError("Invalid Outing: no activities or reservations")

        return max(candidates)


class OutingActivityOrm(Base, TimedEventMixin, GetOneByIdMixin):
    """Pivot table between `outings` and activity sources"""

    __tablename__ = "outing_activities"

    id: Mapped[UUID] = mapped_column(server_default=PG_UUID_EXPR, primary_key=True)
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


class OutingReservationOrm(Base, TimedEventMixin, GetOneByIdMixin):
    """Pivot table between `outings` and reservation sources"""

    __tablename__ = "outing_reservations"

    id: Mapped[UUID] = mapped_column(server_default=PG_UUID_EXPR, primary_key=True)
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
