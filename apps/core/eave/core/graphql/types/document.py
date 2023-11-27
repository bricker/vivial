from typing import Optional
import strawberry.federation as sb

@sb.type
class DocumentSearchResult:
    title: str = sb.field()
    url: Optional[str] = sb.field()

@sb.input
class DocumentInput:
    title: str = sb.field()
    content: str = sb.field()
    parent: Optional["DocumentInput"] = sb.field()

@sb.type
class UpsertDocumentMutationResult(MutationResult):
    team: Team
    subscriptions: list[Subscription]
    document_reference: DocumentReference

class DocumentReferenceMutationResult(MutationResult):
    document_reference: DocumentReference
