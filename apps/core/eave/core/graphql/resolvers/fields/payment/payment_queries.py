import strawberry


@strawberry.type
class PaymentQueries:
    @strawberry.field
    def placeholder(self) -> None:
        return None
