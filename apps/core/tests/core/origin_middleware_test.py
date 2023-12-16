from http import HTTPStatus
import http
from eave.stdlib.core_api.models.error import ErrorResponse

from eave.stdlib.core_api.operations.slack import GetSlackInstallation
from eave.stdlib.core_api.operations.status import Status
from eave.stdlib.headers import EAVE_ORIGIN_HEADER


from .base import BaseTestCase


# TODO: Separate tests for testing response status codes. By default, the HTTP client used for tests raises app exceptions.
# https://github.com/encode/httpx/blob/a682f6f1c7f1c5e10c66ae5bef139aea37ef0c4e/httpx/_transports/asgi.py#L71
class TestOriginMiddleware(BaseTestCase):
    async def test_origin_bypass(self) -> None:
        response = await self.make_request(
            method=Status.config.method,
            path=Status.config.path,
            headers={EAVE_ORIGIN_HEADER: None},
        )

        assert response.status_code == HTTPStatus.OK

    async def test_missing_origin_header(self) -> None:
        # FIXME: This does raise an error (MissingRequiredHeaderError), but it's caught by Starlette so not registered here
        # if using "assertRaises"
        response = await self.make_request(
            path=GetSlackInstallation.config.path,
            headers={
                EAVE_ORIGIN_HEADER: None,
            },
        )

        response_obj = ErrorResponse(**response.json())
        assert response.status_code == http.HTTPStatus.BAD_REQUEST
        assert response_obj.status_code == http.HTTPStatus.BAD_REQUEST
        assert response_obj.error_message == http.HTTPStatus.BAD_REQUEST.phrase

    async def test_invalid_origin(self) -> None:
        response = await self.make_request(
            path=GetSlackInstallation.config.path,
            headers={
                EAVE_ORIGIN_HEADER: self.anystr("invalid origin"),
            },
        )

        response_obj = ErrorResponse(**response.json())
        assert response.status_code == http.HTTPStatus.BAD_REQUEST
        assert response_obj.status_code == http.HTTPStatus.BAD_REQUEST
        assert response_obj.error_message == http.HTTPStatus.BAD_REQUEST.phrase
