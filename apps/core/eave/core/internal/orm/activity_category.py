# from enum import StrEnum
# import hashlib
# import hmac
# import os
# import re
# import uuid
# from dataclasses import dataclass
# from datetime import datetime
# from typing import Literal, Self
# from uuid import UUID

# from sqlalchemy import ForeignKeyConstraint, Index, PrimaryKeyConstraint, ScalarResult, Select, func, select
# from sqlalchemy.ext.asyncio import AsyncSession
# from sqlalchemy.orm import Mapped, mapped_column

# from eave.stdlib.util import b64encode

# from .base import Base
# from .util import PG_UUID_EXPR

# class ActivityCategoryOrm(Base):
#     __tablename__ = "activity_categories"
#     __table_args__ = (
#         PrimaryKeyConstraint("id"),
#         ForeignKeyConstraint(
#             ["parent_category_id"],
#             ["activity_categories.id"],
#         )
#     )

#     id: Mapped[UUID] = mapped_column(server_default=PG_UUID_EXPR)
#     name: Mapped[str] = mapped_column()
#     parent_category_id: Mapped[UUID | None] = mapped_column(server_default=None)
#     eventbrite_category_id: Mapped[str | None] = mapped_column(server_default=None)
#     eventbrite_subcategory_id: Mapped[str | None] = mapped_column(server_default=None)
#     created: Mapped[datetime] = mapped_column(server_default=func.current_timestamp())
#     updated: Mapped[datetime | None] = mapped_column(server_default=None, onupdate=func.current_timestamp())

#     @classmethod
#     async def create(
#         cls,
#         session: AsyncSession,
#         name: str,
#         parent_category_id: UUID | None = None,
#         eventbrite_category_id: str | None = None,
#         eventbrite_subcategory_id: str | None = None,
#     ) -> Self:
#         obj = cls(
#             name=name,
#             parent_category_id=parent_category_id,
#             eventbrite_category_id=eventbrite_category_id,
#             eventbrite_subcategory_id=eventbrite_subcategory_id,
#         )

#         session.add(obj)
#         await session.flush()
#         return obj
