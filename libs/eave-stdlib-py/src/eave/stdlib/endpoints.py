import eave.stdlib.core_api.operations.status as status

from .config import shared_config


def status_payload() -> status.Status.ResponseBody:
    return status.Status.ResponseBody(
        service=shared_config.app_service,
        version=shared_config.app_version,
        status="OK",
    )
