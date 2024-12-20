import strawberry
import stripe


@strawberry.type
class PaymentIntent:
    id: str
    client_secret: str


@strawberry.type
class CustomerSession:
    client_secret: str


@strawberry.type
class PaymentCard:
    brand: str
    last4: str
    exp_month: int
    exp_year: int


@strawberry.type
class PaymentMethod:
    id: str
    card: PaymentCard | None

    @classmethod
    def from_stripe(cls, stripe_payment_method: stripe.PaymentMethod) -> "PaymentMethod":
        return PaymentMethod(
            id=stripe_payment_method.id,
            card=PaymentCard(
                brand=stripe_payment_method.card.brand,
                last4=stripe_payment_method.card.last4,
                exp_month=stripe_payment_method.card.exp_month,
                exp_year=stripe_payment_method.card.exp_year,
            )
            if stripe_payment_method.card
            else None,
        )
