from typing import Awaitable, Callable, cast
from aiohttp.compression_utils import ZLibDecompressor
from aiohttp.hdrs import METH_PATCH, METH_POST, METH_PUT
import asgiref.typing
from eave.stdlib.api_util import get_header_value
from eave.stdlib.exceptions import BadRequestError, LengthRequiredError, MissingRequiredHeaderError, RequestEntityTooLargeError, UnprocessableEntityError
from eave.stdlib.headers import ENCODING_GZIP
from eave.stdlib.request_state import EaveRequestState
import starlette.types
from starlette.requests import Request
import aiohttp
from .base import EaveASGIMiddleware

_REQUEST_BODY_MAX_SIZE = 1 * pow(10, 6) # 1mb

_BODY_METHODS = [
    METH_POST,
    METH_PUT,
    METH_PATCH,
]

class ReadBodyASGIMiddleware(EaveASGIMiddleware):
    async def process_request(
        self,
        scope: asgiref.typing.HTTPScope,
        receive: asgiref.typing.ASGIReceiveCallable,
        send: asgiref.typing.ASGISendCallable,
        request: Request,
        state: EaveRequestState,
        continue_request: Callable[[], Awaitable[None]],
    ) -> None:
        encoding = get_header_value(scope=scope, name=aiohttp.hdrs.CONTENT_ENCODING)
        content_length_header = get_header_value(scope=scope, name=aiohttp.hdrs.CONTENT_LENGTH)

        body = b""

        if scope["method"] in _BODY_METHODS:
            # We only read and validate the body for POST, PUT, and PATCH.
            # For anything else, we remove the body from the request (i.e. set it to empty string)
            if not content_length_header:
                raise LengthRequiredError()

            if int(content_length_header) > _REQUEST_BODY_MAX_SIZE:
                raise RequestEntityTooLargeError()

            # We use `request.stream()` instead of `request.body()` (which just uses `stream()` internally) so we can do the body size check.
            async for chunk in request.stream():
                body += chunk
                if len(body) > _REQUEST_BODY_MAX_SIZE:
                    raise RequestEntityTooLargeError()

            if len(body) != int(content_length_header):
                raise BadRequestError("Invalid request body.")

            # Note: we currently only support gzip compression
            if encoding and ENCODING_GZIP in encoding:
                decompressor = ZLibDecompressor(encoding=encoding)
                body = await decompressor.decompress(body, max_length=_REQUEST_BODY_MAX_SIZE)

        # Then overwrite ASGI receive messages to set the decompressed body for all downstream request handlers.
        # Without this, the next request handler that calls `await request.body()` would get the compressed data again.
        async def dummy_receive() -> asgiref.typing.ASGIReceiveEvent:
            return {
                "type": "http.request",
                "body": body,
                "more_body": False,
            }

        await self.app(scope, dummy_receive, send)
