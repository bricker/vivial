import abc
import json
import typing

# These values are dependent on the eave browser js client implementation and MUST change
# if those values change in the js client
COOKIE_PREFIX = "_eave_"
CONTEXT_NAME = COOKIE_PREFIX + "context"


class BaseCorrelationContext(abc.ABC):
    @abc.abstractmethod
    def get(self, key: str) -> typing.Any: ...

    @abc.abstractmethod
    def set(self, key: str, value: typing.Any) -> None: ...

    def to_json(self) -> str:
        """Convert entirity of storage to JSON string"""
        return json.dumps(self.to_dict())

    @abc.abstractmethod
    def to_dict(self) -> dict[str, typing.Any]:
        """Convert entirity of storage to dict"""
        ...

    @abc.abstractmethod
    def to_cookie(self) -> str:
        """Convert just CONTEXT_NAME dict to URL encoded cookie string"""
        ...

    @abc.abstractmethod
    def from_cookies(self, cookies: dict[str, str]) -> None: ...
