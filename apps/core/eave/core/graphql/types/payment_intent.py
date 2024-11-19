import strawberry


@strawberry.type
class PaymentIntent:
    client_secret: str
