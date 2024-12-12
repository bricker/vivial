from uuid import UUID
import strawberry


@strawberry.type
class PaymentIntent:
    id: str
    client_secret: str
