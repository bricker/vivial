import abc
import json
import typing

# These values are dependent on the eave browser js client implementation and MUST change
# if those values change in the js client
COOKIE_PREFIX = "_eave_"
CONTEXT_NAME = COOKIE_PREFIX + "context"


class BaseCorrelationContext(abc.ABC):
    @abc.abstractmethod
    def get(self, key: str) -> typing.Any:
        """Get a value from storage"""
        ...

    @abc.abstractmethod
    def set(self, key: str, value: typing.Any) -> None:
        """Set a value in storage CONTEXT_NAME dict"""
        ...

    def to_json(self) -> str:
        """Convert entirity of storage to JSON string"""
        return json.dumps(self.to_dict())

    @abc.abstractmethod
    def to_dict(self) -> dict[str, typing.Any]:
        """Convert entirity of storage to dict"""
        ...

    @abc.abstractmethod
    def get_context_cookie(self) -> str:
        """
        Convert just CONTEXT_NAME dict to URL encoded cookie string.

        Only the CONTEXT_NAME dict value is allowed to be updated via this API,
        so no other storage values should need to be forwarded.
        """
        ...

    @abc.abstractmethod
    def from_cookies(self, cookies: dict[str, str]) -> None: ...
