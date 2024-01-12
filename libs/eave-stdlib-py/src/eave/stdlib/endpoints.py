import eave.stdlib.core_api.operations.status as status

from .config import SHARED_CONFIG


def status_payload() -> status.Status.ResponseBody:
    return status.Status.ResponseBody(
        service=SHARED_CONFIG.app_service,
        version=SHARED_CONFIG.app_version,
        status="OK",
    )
