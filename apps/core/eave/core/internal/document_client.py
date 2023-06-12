import abc
from dataclasses import dataclass
from typing import Optional, Protocol

from eave.stdlib.core_api.models.documents import DocumentInput
from eave.stdlib.core_api.models.documents import DocumentSearchResult
from eave.stdlib.logging import LogContext


@dataclass
class DocumentMetadata:
    """
    This is effectively the same as DocumentReferenceOrm, but without all the ORM stuff,
    which keeps it lightweight and also avoids a circular dependency between this file and the ORM file.
    """

    id: str
    url: Optional[str]


class DocumentClient(Protocol):
    @abc.abstractmethod
    async def create_document(self, *, input: DocumentInput, ctx: Optional[LogContext] = None) -> DocumentMetadata:
        ...

    @abc.abstractmethod
    async def update_document(self, *, input: DocumentInput, document_id: str, ctx: Optional[LogContext] = None) -> DocumentMetadata:
        ...

    @abc.abstractmethod
    async def search_documents(self, *, query: str, ctx: Optional[LogContext] = None) -> list[DocumentSearchResult]:
        ...

    @abc.abstractmethod
    async def delete_document(self, *, document_id: str, ctx: Optional[LogContext] = None) -> None:
        ...
