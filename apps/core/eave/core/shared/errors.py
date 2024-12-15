import strawberry


@strawberry.type
class ValidationError:
    subject: str
    field: str
