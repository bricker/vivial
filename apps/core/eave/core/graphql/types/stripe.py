import strawberry


@strawberry.type
class PaymentIntent:
    id: str
    client_secret: str

@strawberry.type
class CustomerSession:
    client_secret: str
