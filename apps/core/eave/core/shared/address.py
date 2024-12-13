import strawberry


@strawberry.type
class Address:
    address1: str | None
    address2: str | None
    city: str | None
    state: str | None
    zip: str | None
    country: str | None

    @strawberry.field
    def formatted_multiline(self) -> str:
        return self.formatted_multiline_internal

    @strawberry.field
    def formatted_singleline(self) -> str:
        return self.formatted_singleline_internal

    @property
    def formatted_multiline_internal(self) -> str:
        """Not exposed to GraphQL"""
        out = ""

        if self.address1:
            out += f"{self.address1}"

        if self.address1 and self.address2:
            out += " "

        if self.address2:
            out += f"{self.address2}"

        if not self.city and not self.state and not self.zip:
            return out

        out += "\n"

        if self.city:
            out += f"{self.city}"

        if not self.state and not self.zip:
            return out

        out += ", "

        if self.state:
            out += f"{self.state}"

        if self.state and self.zip:
            out += " "

        if self.zip:
            out += f"{self.zip}"

        return out

    @property
    def formatted_singleline_internal(self) -> str:
        """Not exposed to GraphQL"""
        return self.formatted_multiline_internal.replace("\n", ", ")
