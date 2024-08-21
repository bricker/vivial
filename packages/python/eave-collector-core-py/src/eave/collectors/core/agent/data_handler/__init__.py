from abc import ABC
from typing import Any

from eave.collectors.core.datastructures import Batchable


class DataHandler(ABC):
    def validate_data_type(self, payload: Any) -> bool: ...

    async def send_buffer(self, buffer: list[Batchable]) -> None: ...
