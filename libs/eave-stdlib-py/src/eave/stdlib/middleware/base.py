from abc import ABC, abstractmethod
from typing import cast

import aiohttp
import asgiref.typing
import starlette.types
from aiohttp.compression_utils import ZLibDecompressor
from eave.stdlib.api_util import get_header_value
from eave.stdlib.headers import ENCODING_GZIP
from eave.stdlib.request_state import EaveRequestState


class EaveASGIMiddleware(ABC):
    """
    https://asgi.readthedocs.io/en/latest/specs/www.html#http
    """

    app: asgiref.typing.ASGI3Application

    def __init__(self, app: starlette.types.ASGIApp) -> None:
        self.app = cast(asgiref.typing.ASGI3Application, app)

    @abstractmethod
    async def run(
        self,
        scope: asgiref.typing.Scope,
        receive: asgiref.typing.ASGIReceiveCallable,
        send: asgiref.typing.ASGISendCallable,
    ) -> None:
        ...

    async def __call__(
        self, scope: starlette.types.Scope, receive: starlette.types.Receive, send: starlette.types.Send
    ) -> None:
        await self.run(
            scope=cast(asgiref.typing.Scope, scope),
            receive=cast(asgiref.typing.ASGIReceiveCallable, receive),
            send=cast(asgiref.typing.ASGISendCallable, send),
        )

    @staticmethod
    async def read_body(scope: asgiref.typing.HTTPScope, receive: asgiref.typing.ASGIReceiveCallable) -> bytes:
        eave_state = EaveRequestState.load(scope=scope)
        if not eave_state.raw_request_body:
            body: bytes = b""

            while True:
                # https://asgi.readthedocs.io/en/latest/specs/www.html#request-receive-event
                message = await receive()
                assert message["type"] == "http.request"
                chunk: bytes = message.get("body", b"")
                body += chunk

                if message.get("more_body", False) is False:
                    break

            encoding = get_header_value(scope=scope, name=aiohttp.hdrs.CONTENT_ENCODING)

            if encoding == ENCODING_GZIP:
                decompressor = ZLibDecompressor(encoding=encoding)
                decompressed_body = await decompressor.decompress(body)
                eave_state.raw_request_body = decompressed_body
            else:
                eave_state.raw_request_body = body

            # Note: we currently do not support other compression encodings.

        return eave_state.raw_request_body
