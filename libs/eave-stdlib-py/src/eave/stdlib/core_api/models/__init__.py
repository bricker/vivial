import pydantic


class BaseResponseModel(pydantic.BaseModel):
    class Config:
        orm_mode = True


class BaseInputModel(pydantic.BaseModel):
    class Config:
        extra = pydantic.Extra.forbid
