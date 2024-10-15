from uuid import UUID

import strawberry as sb


@sb.type
class MutationResult:
    eave_request_id: UUID
