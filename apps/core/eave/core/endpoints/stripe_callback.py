from uuid import UUID
from asgiref.typing import HTTPScope
from eave.stdlib.config import SHARED_CONFIG
from eave.stdlib.cookies import EAVE_ACCESS_TOKEN_COOKIE_NAME
from eave.stdlib.exceptions import UnauthorizedError
from eave.stdlib.headers import MIME_TYPE_JSON
from eave.stdlib.http_endpoint import HTTPEndpoint
from eave.stdlib.jwt import JWTPurpose, validate_jws_or_exception
from eave.stdlib.logging import LogContext
from eave.stdlib.status import status_payload
from starlette.requests import Request
from starlette.responses import RedirectResponse, Response


import http

from eave.core.config import JWT_AUDIENCE, JWT_ISSUER


class StripeCallbackEndpoint(HTTPEndpoint):
    async def handle(self, request: Request, scope: HTTPScope, ctx: LogContext) -> Response:
        encoded_jws = request.cookies.get(EAVE_ACCESS_TOKEN_COOKIE_NAME)
        if encoded_jws:
            jws = validate_jws_or_exception(
                encoded_jws=encoded_jws,
                expected_audience=JWT_AUDIENCE,
                expected_issuer=JWT_ISSUER,
                expected_purpose=JWTPurpose.ACCESS,
            )

            authenticated_account_id = UUID(jws.payload.sub)
            print(authenticated_account_id)
        else:
            raise UnauthorizedError()

        # payment_intent = request.query_params.get("payment_intent")
        # payment_intent_client_secret = request.query_params.get("payment_intent_client_secret")
        # redirect_status = request.query_params.get("redirect_status")

        # TODO: Update database with payment intent information
        return RedirectResponse(
            url=f"{SHARED_CONFIG.eave_dashboard_base_url_public}/booking-confirmation?bookingId=TKTKTK"
        )
