from uuid import UUID

from sqlalchemy import ForeignKey, ForeignKeyConstraint, PrimaryKeyConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from eave.core.orm.account import AccountOrm
from eave.core.orm.survey import SurveyOrm
from eave.core.orm.util.mixins import GetOneByIdMixin

from .base import Base
from .util.constants import PG_UUID_EXPR, OnDeleteOption


class OutingOrm(Base, GetOneByIdMixin):
    __tablename__ = "outings"
    __table_args__ = (
    )

    id: Mapped[UUID] = mapped_column(primary_key=True, server_default=PG_UUID_EXPR)
    visitor_id: Mapped[UUID] = mapped_column()

    survey_id: Mapped[UUID] = mapped_column(ForeignKey(f"{SurveyOrm.__tablename__}.id", ondelete=OnDeleteOption.CASCADE))
    survey: Mapped[SurveyOrm] = relationship()

    account_id: Mapped[UUID | None] = mapped_column(ForeignKey(f"{AccountOrm.__tablename__}.id", ondelete=OnDeleteOption.SET_NULL))
    account: Mapped[AccountOrm] = relationship()

    @classmethod
    def build(
        cls,
        *,
        visitor_id: UUID,
        survey_id: UUID,
        account_id: UUID | None = None,
    ) -> "OutingOrm":
        obj = OutingOrm(
            visitor_id=visitor_id,
            account_id=account_id,
            survey_id=survey_id,
        )

        return obj
