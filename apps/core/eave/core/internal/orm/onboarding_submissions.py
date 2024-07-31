from datetime import datetime
from typing import Self, TypedDict, Unpack
from uuid import UUID

import sqlalchemy
import sqlalchemy.dialects.postgresql
from sqlalchemy import Select, func, select, text
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import Mapped, mapped_column

import eave.stdlib.util
from eave.stdlib.core_api.models.onboarding_submissions import OnboardingSubmission

from .base import Base
from .util import UUID_DEFAULT_EXPR, make_team_composite_pk, make_team_fk


class OnboardingSubmissionOrm(Base):
    __tablename__ = "onboarding_submissions"

    __table_args__ = (
        make_team_composite_pk(table_name="onboarding_submissions"),
        make_team_fk(),
    )

    id: Mapped[UUID] = mapped_column(primary_key=True, server_default=UUID_DEFAULT_EXPR)
    team_id: Mapped[UUID] = mapped_column(primary_key=True)
    languages: Mapped[list[str]] = mapped_column(
        type_=sqlalchemy.dialects.postgresql.ARRAY(
            item_type=sqlalchemy.types.String,
            dimensions=1,
        ),
        server_default=text("'{}'"),
    )
    """List of programming languages used by the application(s)"""
    platforms: Mapped[list[str]] = mapped_column(
        type_=sqlalchemy.dialects.postgresql.ARRAY(
            item_type=sqlalchemy.types.String,
            dimensions=1,
        ),
        server_default=text("'{}'"),
    )
    """List of application platforms (web, android, etc.)"""
    frameworks: Mapped[list[str]] = mapped_column(
        type_=sqlalchemy.dialects.postgresql.ARRAY(
            item_type=sqlalchemy.types.String,
            dimensions=1,
        ),
        server_default=text("'{}'"),
    )
    """List of key libraries/frameworks used by the application (django, express.js, etc.)"""
    databases: Mapped[list[str]] = mapped_column(
        type_=sqlalchemy.dialects.postgresql.ARRAY(
            item_type=sqlalchemy.types.String,
            dimensions=1,
        ),
        server_default=text("'{}'"),
    )
    """List of database software used by the application"""
    third_party_libs: Mapped[list[str]] = mapped_column(
        type_=sqlalchemy.dialects.postgresql.ARRAY(
            item_type=sqlalchemy.types.String,
            dimensions=1,
        ),
        server_default=text("'{}'"),
    )
    """List of 3rd party libs/services used by the application (openAI, AWS, etc.)"""
    created: Mapped[datetime] = mapped_column(server_default=func.current_timestamp())
    updated: Mapped[datetime | None] = mapped_column(server_default=None, onupdate=func.current_timestamp())

    @classmethod
    async def create(cls, session: AsyncSession, team_id: UUID, submission: OnboardingSubmission) -> Self:
        obj = cls(
            team_id=team_id,
            languages=submission.languages,
            platforms=submission.platforms,
            frameworks=submission.frameworks,
            databases=submission.databases,
            third_party_libs=submission.third_party_libs,
        )
        session.add(obj)
        await session.flush()
        return obj

    @property
    def api_model(self) -> OnboardingSubmission:
        return OnboardingSubmission.from_orm(self)

    class QueryParams(TypedDict):
        team_id: UUID | str

    @classmethod
    def query(cls, **kwargs: Unpack[QueryParams]) -> Select[tuple[Self]]:
        team_id = eave.stdlib.util.ensure_uuid(kwargs["team_id"])
        lookup = select(cls).where(cls.team_id == team_id)
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

    def is_qualified(self) -> bool:
        """
        Check if this onboarding form submission qualifies a
        team for Eave usage.
        """
        # CURRENTLY DENY ALL
        # return False

        # convert all answers to lowercase for easier comparison
        return all(
            [
                "python" in map(to_lower, self.languages),
                "web_app" in map(to_lower, self.platforms),
                "starlette" in map(to_lower, self.frameworks) or "fast_api" in map(to_lower, self.frameworks),
                "openai" in map(to_lower, self.third_party_libs),
            ]
        )


def to_lower(s: str) -> str:
    return s.lower()
