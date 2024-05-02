import abc
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

    @abc.abstractmethod
    def to_json(self) -> str: ...

    @abc.abstractmethod
    def to_dict(self) -> dict[str, typing.Any]: ...

    @abc.abstractmethod
    def to_cookie(self) -> str: ...

    @abc.abstractmethod
    def from_cookies(self, cookies: dict[str, str]) -> None: ...
