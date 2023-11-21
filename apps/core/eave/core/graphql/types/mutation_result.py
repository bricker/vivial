from uuid import UUID
import strawberry.federation as sb

@sb.type
class MutationResult:
    eave_request_id: UUID
