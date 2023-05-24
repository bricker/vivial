import abc
from dataclasses import dataclass
from typing import Optional, Protocol
from eave.stdlib.core_api.models import DocumentSearchResult

import eave.stdlib.core_api.operations as eave_ops


@dataclass
class DocumentMetadata:
    """
    This is effectively the same as DocumentReferenceOrm, but without all the ORM stuff,
    which keeps it lightweight and also avoids a circular dependency between this file and the ORM file.
    """

    id: str
    url: Optional[str]


class DocumentDestination(Protocol):
    @abc.abstractmethod
    async def create_document(self, input: eave_ops.DocumentInput) -> DocumentMetadata:
        ...

    @abc.abstractmethod
    async def update_document(self, input: eave_ops.DocumentInput, document_id: str) -> DocumentMetadata:
        ...

    @abc.abstractmethod
    async def search_documents(self, query: str) -> list[DocumentSearchResult]:
        ...

    @abc.abstractmethod
    async def delete_document(self, document_id: str) -> None:
        ...
