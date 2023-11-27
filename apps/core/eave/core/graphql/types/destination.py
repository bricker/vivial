import strawberry.federation as sb

@sb.type
class Destination:
    confluence_destination: Optional[ConfluenceDestination]

@sb.type
class ConfluenceDestinationMutationResult(MutationResult):
    confluence_destination: ConfluenceDestination

@sb.input
class ConfluenceDestinationInput:
    space_key: str = sb.field()