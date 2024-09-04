import uuid

from eave.stdlib.core_api.models import BaseResponseModel


class DataCollectorConfig(BaseResponseModel):
    id: uuid.UUID
    # TODO
