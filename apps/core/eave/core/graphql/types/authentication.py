import strawberry as sb

@sb.input
class Credentials:
    email: str = sb.field()
    password: str = sb.field()

@sb.type
class Credentials:
    email: str = sb.field()
    password: str = sb.field()
