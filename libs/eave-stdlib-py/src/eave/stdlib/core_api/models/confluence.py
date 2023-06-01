import pydantic

from eave.stdlib.core_api.models import BaseResponseModel


class ConfluenceInstallation(BaseResponseModel):
    id: pydantic.UUID4
    team_id: pydantic.UUID4
