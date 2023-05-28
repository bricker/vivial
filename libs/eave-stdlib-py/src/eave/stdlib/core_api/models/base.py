import pydantic

class EaveBaseModel(pydantic.BaseModel):
    class Config:
        extra = pydantic.Extra.forbid
