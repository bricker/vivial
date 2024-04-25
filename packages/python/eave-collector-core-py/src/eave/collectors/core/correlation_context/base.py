import abc
import typing


class BaseCorrelationContext(abc.ABC):
    @abc.abstractmethod
    def get(self, key: str) -> typing.Any: ...

    @abc.abstractmethod
    def set(self, key: str, value: typing.Any) -> None: ...

    @abc.abstractmethod
    def to_json(self) -> str: ...

    # @abc.abstractmethod
    # def to_cookie(self) -> str: ...

    # @classmethod
    # @abc.abstractmethod
    # def from_cookies(cls, cookies) -> typing.Self: ...
