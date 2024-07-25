from datetime import datetime
from typing import Self, TypedDict, Unpack
from uuid import UUID

from eave.stdlib.core_api.models.onboarding_submissions import OnboardingSubmission
from sqlalchemy import Select, func, select, JSON
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import Mapped, mapped_column

import eave.stdlib.util

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
    response_data: Mapped[dict] = mapped_column(JSON)
    """JSON object where key is question and value is list of tags"""
    created: Mapped[datetime] = mapped_column(server_default=func.current_timestamp())
    updated: Mapped[datetime | None] = mapped_column(server_default=None, onupdate=func.current_timestamp())

    @classmethod
    async def create(
        cls,
        session: AsyncSession,
        team_id: UUID,
        response_data: dict[str, list[str]],
    ) -> Self:
        obj = cls(
            team_id=team_id,
            response_data=response_data,
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

    def is_qualified(self) -> bool:
        """
        Check if this onboarding form submission qualifies a
        team for Eave usage.
        """
        form_responses = self.response_data.copy() #json.loads(json.dumps(self.response_data))
        # convert all answers to lowercase for easier comparison
        for question_key, response_list in form_responses.items():
            form_responses[question_key] = [resp.lower() for resp in response_list]

        # TODO: standardize question keys???
        return all(
            [
                "python" in form_responses["languages"],
                "browser app" in form_responses["platform"],
                "starlette" in form_responses["frameworks"] or "fast api" in form_responses["libraries"],
                "openai" in form_responses["third_party"],
            ]
        )
