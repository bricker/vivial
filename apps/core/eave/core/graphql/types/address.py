import strawberry

from eave.core.lib.address import Address, BaseAddress, format_address


@strawberry.type(name="Address")
class GraphQLAddress(BaseAddress):
    @strawberry.field
    def formatted_multiline(self) -> str:
        return format_address(self, singleline=False)

    @strawberry.field
    def formatted_singleline(self) -> str:
        return format_address(self, singleline=True)

    @classmethod
    def from_address(cls, address: Address) -> "GraphQLAddress":
        """
        Convert a plain Address object to a GraphQLAddress object
        """
        return GraphQLAddress(
            address1=address.address1,
            address2=address.address2,
            city=address.city,
            state=address.state,
            zip_code=address.zip_code,
            country=address.country,
        )

    def to_address(self) -> Address:
        """
        Convert a GraphQLAddress object to a plain Address object.
        """
        return Address(
            address1=self.address1,
            address2=self.address2,
            city=self.city,
            state=self.state,
            zip_code=self.zip_code,
            country=self.country,
        )
