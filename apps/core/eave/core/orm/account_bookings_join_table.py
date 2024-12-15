from sqlalchemy import Column, ForeignKey, Table

from eave.core.orm.base import Base
from eave.core.orm.util.constants import OnDeleteOption

ACCOUNT_BOOKINGS_JOIN_TABLE = Table(
    "account_bookings",
    Base.metadata,
    Column("booking_id", ForeignKey("bookings.id", ondelete=OnDeleteOption.CASCADE.value)),
    Column("account_id", ForeignKey("accounts.id", ondelete=OnDeleteOption.CASCADE.value)),
)
