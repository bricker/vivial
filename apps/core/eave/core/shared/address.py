import strawberry


@strawberry.type
class Address:
    address1: str | None
    address2: str | None
    city: str | None
    state: str | None
    zip_code: str | None
    country: str | None
    formatted_multiline: str
    formatted_singleline: str

    def __init__(self, *,
        address1: str | None,
        address2: str | None,
        city: str | None,
        state: str | None,
        zip_code: str | None,
        country: str | None,
    ) -> None:
        self.address1 = address1
        self.address2 = address2
        self.city = city
        self.state = state
        self.zip_code = zip_code
        self.country = country

        # We do this because strawberry looks at the dataclass __annotations__ property, but we don't want it to be
        # passed into the initializer.
        # The slight problem with this is that if some property in this instance is updated, the formatted address
        # won't reflect that.
        # The alternative is to have separate functions, one for the resolver and
        formatted_multiline = _format_address_multiline(self)
        self.formatted_multiline = formatted_multiline
        self.formatted_singleline = formatted_multiline.replace("\n", ", ")


def _format_address_multiline(address: Address) -> str:
        out = ""

        if address.address1:
            out += f"{address.address1}"

        if address.address1 and address.address2:
            out += " "

        if address.address2:
            out += f"{address.address2}"

        if not address.city and not address.state and not address.zip_code:
            return out

        out += "\n"

        if address.city:
            out += f"{address.city}"

        if not address.state and not address.zip_code:
            return out

        out += ", "

        if address.state:
            out += f"{address.state}"

        if address.state and address.zip_code:
            out += " "

        if address.zip_code:
            out += f"{address.zip_code}"

        return out
