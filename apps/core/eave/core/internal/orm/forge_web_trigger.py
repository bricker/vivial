import json
import typing
import uuid
from datetime import datetime
from typing import Mapping, NotRequired, Optional, Required, Self, Sequence, Tuple, TypedDict, Unpack
from uuid import UUID

import eave.stdlib.core_api
from sqlalchemy import Index, PrimaryKeyConstraint, Select, func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import Mapped, mapped_column

from .. import database as eave_db
from ..destinations import confluence as confluence_destination
from ..oauth import atlassian as atlassian_oauth
from .base import Base
from .util import UUID_DEFAULT_EXPR, make_team_composite_pk, make_team_fk, make_team_composite_fk

class ForgeWebTriggerOrm(Base):
    __tablename__ = "forge_web_triggers"
    __table_args__ = (
        make_team_fk(),
        make_team_composite_fk("forge_installation_id", "forge_installations"),
        PrimaryKeyConstraint(
            "team_id",
            "forge_installation_id",
            "id",
        ),
    )

    team_id: Mapped[UUID] = mapped_column()
    forge_installation_id: Mapped[UUID] = mapped_column()
    id: Mapped[UUID] = mapped_column(server_default=UUID_DEFAULT_EXPR)
    webtrigger_key: Mapped[str] = mapped_column()
    webtrigger_url: Mapped[str] = mapped_column()
    created: Mapped[datetime] = mapped_column(server_default=func.current_timestamp())
    updated: Mapped[Optional[datetime]] = mapped_column(server_default=None, onupdate=func.current_timestamp())

    class _selectparams(TypedDict):
        webtrigger_key: NotRequired[str]
        team_id: Required[uuid.UUID]
        forge_installation_id: Required[uuid.UUID]

    @classmethod
    def _build_select(cls, **kwargs: Unpack[_selectparams]) -> Select[Tuple[Self]]:
        lookup = select(cls).limit(1)

        team_id = kwargs["team_id"]
        forge_installation_id = kwargs["forge_installation_id"]

        lookup = (
            lookup
            .where(cls.team_id == team_id)
            .where(cls.forge_installation_id == forge_installation_id)
        )

        if webtrigger_key := kwargs.get("webtrigger_key"):
            lookup = lookup.where(cls.webtrigger_key == webtrigger_key)

        assert lookup.whereclause is not None
        return lookup

    @classmethod
    async def query(cls, session: AsyncSession, **kwargs: Unpack[_selectparams]) -> Sequence[Self]:
        lookup = cls._build_select(**kwargs)
        results = (await session.scalars(lookup)).all()
        return results


    @classmethod
    async def one_or_exception(cls, session: AsyncSession, **kwargs: Unpack[_selectparams]) -> Self:
        lookup = cls._build_select(**kwargs)
        result = (await session.scalars(lookup)).one()
        return result

    @classmethod
    async def one_or_none(cls, session: AsyncSession, **kwargs: Unpack[_selectparams]) -> Self | None:
        lookup = cls._build_select(**kwargs)
        result = await session.scalar(lookup)
        return result

    @classmethod
    async def upsert(
        cls,
        session: AsyncSession,
        team_id: uuid.UUID,
        forge_installation_id: uuid.UUID,
        input: eave.stdlib.core_api.operations.forge.ForgeWebTriggerInput,
    ) -> Self:
        obj = await cls.one_or_none(
            session=session,
            team_id=team_id,
            forge_installation_id=forge_installation_id,
            webtrigger_key=input.webtrigger_key,
        )

        if obj:
            obj.update(session=session, input=input)
        else:
            obj = cls(
                team_id=team_id,
                forge_installation_id=forge_installation_id,
                webtrigger_key=input.webtrigger_key,
                webtrigger_url=input.webtrigger_url,
            )

        session.add(obj)
        await session.flush()
        return obj

    @classmethod
    def mapping(cls, triggers: Sequence[Self]) -> Mapping[str, eave.stdlib.core_api.models.forge.ForgeWebTrigger]:
        return {
            trigger.webtrigger_key: eave.stdlib.core_api.models.forge.ForgeWebTrigger.from_orm(trigger)
            for trigger in triggers
        }


    def update(
        self,
        session: AsyncSession,
        input: eave.stdlib.core_api.operations.forge.ForgeWebTriggerInput,
    ) -> Self:
        """
        Updates the given attributes.
        The `session` parameter is not used, but is requested to encourage the developer to use this method
        in the intended context of a database session.
        """

        # webtrigger_key cannot be updated on this model
        self.webtrigger_url = input.webtrigger_url
        return self
