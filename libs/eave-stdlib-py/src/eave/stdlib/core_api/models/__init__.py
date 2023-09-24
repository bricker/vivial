import pydantic
from pydantic import ConfigDict


class BaseResponseModel(pydantic.BaseModel):
    model_config = ConfigDict(from_attributes=True)


class BaseInputModel(pydantic.BaseModel):
    model_config = ConfigDict(extra=pydantic.Extra.forbid)
