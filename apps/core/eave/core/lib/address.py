import dataclasses
from typing import Any


@dataclasses.dataclass(kw_only=True)
class BaseAddress:
    """
    This base class defines the common address fields.
    It is used by both GraphQLAddress and Address classes.
    They are separate because GraphQLAddress has some special fields that can't be
    serialized correctly for insert into the database.
    """

    address1: str | None
    address2: str | None
    city: str | None
    state: str | None
    zip_code: str | None
    country: str | None


class Address(BaseAddress):
    """
    A plain address for internal (database) use.
    For GraphQL, use GraphQLAddress.
    """

    def __init__(
        self,
        *,
        address1: str | None = None,
        address2: str | None = None,
        city: str | None = None,
        state: str | None = None,
        zip_code: str | None = None,
        country: str | None = None,
        **kwargs: Any,  # In case anything else was in this field in the database
    ) -> None:
        # We define our own init function because this dataclass is populated from a JSON object in the database,
        # and if there are any extra fields, we'd get an error "unexpected keyword argument"
        super().__init__(
            address1=address1,
            address2=address2,
            city=city,
            state=state,
            zip_code=zip_code,
            country=country,
        )


def format_address(address: BaseAddress, *, singleline: bool = False) -> str:
    line1 = ", ".join(s for s in [address.address1, address.address2] if s)

    line2 = ", ".join(s for s in [address.city, address.state] if s)

    if address.zip_code:
        if line2:
            line2 += " "
        line2 += address.zip_code

    condensed = [s for s in [line1, line2] if s]
    if singleline:
        return ", ".join(condensed)
    else:
        return "\n".join(condensed)
