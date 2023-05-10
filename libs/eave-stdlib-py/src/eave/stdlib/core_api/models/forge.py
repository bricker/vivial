import pydantic
import typing
from .base import EaveBaseModel

class ForgeInstallation(EaveBaseModel):
    id: pydantic.UUID4
    forge_app_id: str
    forge_app_version: str
    forge_app_installation_id: str
    forge_app_installer_account_id: str
    confluence_space_key: typing.Optional[str]

    class Config:
        orm_mode = True

class ForgeWebTrigger(EaveBaseModel):
    id: pydantic.UUID4
    webtrigger_key: str
    webtrigger_url: str

    class Config:
        orm_mode = True
