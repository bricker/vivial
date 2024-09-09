from abc import ABC
from typing import TypeVar, Generic

from eave.collectors.core.datastructures import Batchable

T = TypeVar("T", bound=Batchable)
class DataHandler(ABC, Generic[T]):
    async def send_buffer(self, buffer: list[T]) -> None: ...
