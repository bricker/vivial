import dataclasses
import json
from dataclasses import dataclass

from eave.stdlib.config import SHARED_CONFIG


@dataclass(kw_only=True)
class StatusPayload:
    service: str
    version: str
    release_date: str
    status: str

    def json(self) -> str:
        return json.dumps(dataclasses.asdict(self))


def status_payload() -> StatusPayload:
    return StatusPayload(
        service=SHARED_CONFIG.app_service,
        version=SHARED_CONFIG.app_version,
        release_date=SHARED_CONFIG.release_date,
        status="OK",
    )
