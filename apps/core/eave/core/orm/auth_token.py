# from dataclasses import dataclass
# from datetime import datetime
# from typing import Self
# from uuid import UUID, uuid4

# from sqlalchemy import ForeignKeyConstraint, Index, PrimaryKeyConstraint, ScalarResult, Select, func, select
# from sqlalchemy.ext.asyncio import AsyncSession
# from sqlalchemy.orm import Mapped, mapped_column

# from .base import Base
# from .util import PG_UUID_EXPR


# class AuthTokenOrm(Base):
#     __tablename__ = "auth_tokens"
#     __table_args__ = (
#         PrimaryKeyConstraint("id"),
#         ForeignKeyConstraint(
#             ["account_id"],
#             ["accounts.id"],
#             ondelete="CASCADE",
#         ),
#         Index(
#             None,
#             "account_id",
#             "jti",
#         ),
#     )

#     id: Mapped[UUID] = mapped_column(server_default=PG_UUID_EXPR)
#     account_id: Mapped[UUID] = mapped_column()
#     jti: Mapped[UUID] = mapped_column(
#         unique=True
#     )  # This is separate from the `id` so that we can update it for new token pairs.
#     created: Mapped[datetime] = mapped_column(server_default=func.current_timestamp())
#     updated: Mapped[datetime | None] = mapped_column(server_default=None, onupdate=func.current_timestamp())

#     @classmethod
#     async def create(
#         cls,
#         session: AsyncSession,
#         account_id: UUID,
#     ) -> Self:
#         obj = cls(
#             account_id=account_id,
#             jti=uuid4(),
#         )

#         session.add(obj)
#         await session.flush()
#         return obj

#     @dataclass
#     class QueryParams:
#         account_id: UUID
#         jti: UUID

#     @classmethod
#     def _build_query(cls, params: QueryParams) -> Select[tuple[Self]]:
#         lookup = select(cls)
#         lookup = lookup.where(cls.account_id == params.account_id)
#         lookup = lookup.where(cls.jti == params.jti)

#         assert lookup.whereclause is not None, "Invalid parameters"
#         return lookup

#     @classmethod
#     async def query(cls, session: AsyncSession, params: QueryParams) -> ScalarResult[Self]:
#         lookup = cls._build_query(params=params)
#         result = await session.scalars(lookup)
#         return result

#     @classmethod
#     async def one_or_exception(cls, session: AsyncSession, params: QueryParams) -> Self:
#         result = await cls.query(session=session, params=params)
#         return result.one()

#     @classmethod
#     async def one_or_none(cls, session: AsyncSession, params: QueryParams) -> Self | None:
#         result = await cls.query(session=session, params=params)
#         return result.one_or_none()
