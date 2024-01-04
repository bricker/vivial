import gzip
import zlib
import aiohttp
from aiohttp.compression_utils import ZLibDecompressor
from asgiref.typing import ASGI3Application, ASGIReceiveCallable, ASGISendCallable, Scope, HTTPScope
from eave.stdlib.api_util import get_header_value
from eave.stdlib.headers import ENCODING_GZIP

from eave.stdlib.request_state import EaveRequestState


class EaveASGIMiddleware:
    """
    https://asgi.readthedocs.io/en/latest/specs/www.html#http
    """

    app: ASGI3Application

    def __init__(self, app: ASGI3Application) -> None:
        self.app = app

    async def __call__(self, scope: Scope, receive: ASGIReceiveCallable, send: ASGISendCallable) -> None:
        ...

    @staticmethod
    async def read_body(scope: HTTPScope, receive: ASGIReceiveCallable) -> bytes:
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
