from datetime import datetime
from typing import (
    Optional,
    Self,
)
from uuid import UUID

import eave.stdlib.core_api.enums
import eave.stdlib.core_api.models as eave_models
import oauthlib.oauth2.rfc6749.tokens
from sqlalchemy import (
    false,
    func,
    select,
)
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import Mapped, mapped_column, relationship

from . import Base, UUID_DEFAULT_EXPR
from .atlassian_installation import AtlassianInstallationOrm
from .subscription import SubscriptionOrm
from ..destinations import abstract as abstract_destination

class TeamOrm(Base):
    __tablename__ = "teams"

    id: Mapped[UUID] = mapped_column(primary_key=True, server_default=UUID_DEFAULT_EXPR)
    name: Mapped[str]
    document_platform: Mapped[Optional[eave_models.DocumentPlatform]] = mapped_column(
        server_default=None
    )
    created: Mapped[datetime] = mapped_column(server_default=func.current_timestamp())
    updated: Mapped[Optional[datetime]] = mapped_column(server_default=None, onupdate=func.current_timestamp())
    beta_whitelisted: Mapped[bool] = mapped_column(server_default=false())

    subscriptions: Mapped[list[SubscriptionOrm]] = relationship()

    @classmethod
    async def create(cls, session: AsyncSession, name: str, document_platform: Optional[eave_models.DocumentPlatform] = None, beta_whitelisted: bool = False) -> Self:
        obj = cls(
            name=name,
            document_platform=document_platform,
            beta_whitelisted=beta_whitelisted,
        )
        session.add(obj)
        await session.flush()
        return obj

    async def get_document_destination(
        self, session: AsyncSession
    ) -> Optional[abstract_destination.DocumentDestination]:
        match self.document_platform:
            case None:
                return None

            case eave.stdlib.core_api.enums.DocumentPlatform.confluence:
                atlassian_installation = await AtlassianInstallationOrm.one_or_exception(
                    session=session,
                    team_id=self.id,
                )
                return atlassian_installation.confluence_destination

            case eave.stdlib.core_api.enums.DocumentPlatform.google_drive:
                raise NotImplementedError("google drive document destination is not yet implemented.")

            case eave.stdlib.core_api.enums.DocumentPlatform.eave:
                raise NotImplementedError("eave document destination is not yet implemented.")

            case _:
                raise NotImplementedError(f"unsupported document platform: {self.document_platform}")

    @classmethod
    async def one_or_exception(cls, session: AsyncSession, team_id: UUID) -> Self:
        lookup = select(cls).where(cls.id == team_id).limit(1)
        team = (await session.scalars(lookup)).one()  # throws if not exists
        return team
