import atexit
from multiprocessing.connection import Client, Connection
from typing import Any

from .agent import _sockaddr

_client: Connection | None = None


def get_client() -> Connection:
    global _client
    if not _client:
        _client = Client(address=_sockaddr, family="AF_UNIX")
    return _client


def send(obj: Any) -> None:
    get_client().send(obj)


def _close() -> None:
    if _client:
        send("EOF")
        _client.close()


atexit.register(_close)
