import strawberry

from eave.core.lib.address import BaseAddress, format_address


@strawberry.type(name="Address")
class GraphQLAddress(BaseAddress):
    @strawberry.field
    def formatted_multiline(self) -> str:
        return format_address(self, singleline=False)

    @strawberry.field
    def formatted_singleline(self) -> str:
        return format_address(self, singleline=True)
