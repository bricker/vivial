
import abc
from dataclasses import dataclass
from typing import Optional, Protocol
import eave.stdlib.core_api.operations as eave_ops
from .. import orm as eave_orm

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
