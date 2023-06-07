from typing import Optional
import aiohttp
import pydantic
from eave.stdlib.core_api.operations import EndpointConfiguration
from ..config import shared_config


class ConfluenceEndpointConfiguration(EndpointConfiguration):
    @property
    def url(self) -> str:
        return f"{shared_config.eave_apps_base}/confluence/api{self.path}"


class ConfluenceEndpoint:
    config: ConfluenceEndpointConfiguration
