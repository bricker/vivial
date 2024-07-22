from datetime import datetime
from typing import Self, TypedDict, Unpack
from urllib.parse import urlparse
from uuid import UUID
import json

import sqlalchemy.dialects.postgresql
import sqlalchemy.types
from sqlalchemy import Select, func, select, text, JSON
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import Mapped, mapped_column

import eave.stdlib.util
from eave.stdlib.core_api.models.team import Team

from .base import Base
from .util import UUID_DEFAULT_EXPR, make_team_composite_pk, make_team_fk


class OnboardingSubmissionOrm(Base):
    __tablename__ = "onboarding_submissions"

    __table_args__ = (
        make_team_composite_pk(table_name="onboarding_submissions"),
        make_team_fk(),
    )

    id: Mapped[UUID] = mapped_column(primary_key=True, server_default=UUID_DEFAULT_EXPR)
    team_id: Mapped[UUID] = mapped_column()
    response_data: Mapped[JSON] = mapped_column()
    """JSON object where key is question and value is list of tags"""
    created: Mapped[datetime] = mapped_column(server_default=func.current_timestamp())
    updated: Mapped[datetime | None] = mapped_column(server_default=None, onupdate=func.current_timestamp())


    @classmethod
    async def create(
        cls,
        session: AsyncSession,
        team_id: uuid.UUID,
        response_data: dict[str, list[str]],
    ) -> Self:
        obj = cls(
            team_id=team_id,
            response_data=response_data,
        )
        session.add(obj)
        await session.flush()
        return obj
    
    def is_qualified(self) -> bool:
        """
        requires all of:
        Python
        Browser App
        Starlette
        OpenAI
        """
        form_responses = json.loads(self.response_data)
        # convert all answers to lowercase for easier comparison
        for question_key, response_list in form_responses.items():
            form_responses[question_key] = [resp.lower() for resp in response_list]

        # TODO: standardize question keys???
        return all(
            "python" in form_responses["languages"],
            "browser app" in form_responses["applications"],
            "starlette" in form_responses["libraries"] or "fast api" in form_responses["libraries"],
            "openai" in form_responses["ai"],
        )
        