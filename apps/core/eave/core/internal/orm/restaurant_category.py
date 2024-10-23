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

# from sqlalchemy import Index, PrimaryKeyConstraint, ScalarResult, Select, func, select, text
# from sqlalchemy.ext.asyncio import AsyncSession
# from sqlalchemy.orm import Mapped, mapped_column
# import sqlalchemy.dialects.postgresql

# from eave.stdlib.util import b64encode

# from .base import Base
# from .util import PG_EMPTY_ARRAY_EXPR, PG_UUID_EXPR

# class RestaurantCategoryOrm(Base):
#     __tablename__ = "restaurant_categories"
#     __table_args__ = (
#         PrimaryKeyConstraint("id"),
#     )

#     id: Mapped[UUID] = mapped_column(server_default=PG_UUID_EXPR)
#     name: Mapped[str] = mapped_column()
#     google_places_keys: Mapped[list[str]] = mapped_column(
#         type_=sqlalchemy.dialects.postgresql.ARRAY(
#             item_type=sqlalchemy.types.String,
#             dimensions=1,
#         ),
#         server_default=PG_EMPTY_ARRAY_EXPR,
#     )
#     created: Mapped[datetime] = mapped_column(server_default=func.current_timestamp())
#     updated: Mapped[datetime | None] = mapped_column(server_default=None, onupdate=func.current_timestamp())

#     @classmethod
#     async def create(
#         cls,
#         session: AsyncSession,
#         name: str,
#         parent_category_id: UUID | None = None,
#     ) -> Self:
#         obj = cls(
#             name=name,
#             parent_category_id=parent_category_id,
#         )

#         session.add(obj)
#         await session.flush()
#         return obj
