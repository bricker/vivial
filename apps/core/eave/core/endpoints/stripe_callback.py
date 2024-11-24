from uuid import UUID

from asgiref.typing import HTTPScope
from starlette.requests import Request
from starlette.responses import RedirectResponse, Response

from eave.core.config import JWT_AUDIENCE, JWT_ISSUER
from eave.stdlib.config import SHARED_CONFIG
from eave.stdlib.cookies import EAVE_ACCESS_TOKEN_COOKIE_NAME
from eave.stdlib.http_exceptions import UnauthorizedError
from eave.stdlib.http_endpoint import HTTPEndpoint
from eave.stdlib.jwt import JWTPurpose, validate_jws_or_exception
from eave.stdlib.logging import LogContext


# class StripeCallbackEndpoint(HTTPEndpoint):
#     async def handle(self, request: Request, scope: HTTPScope, ctx: LogContext) -> Response:
#         encoded_jws = request.cookies.get(EAVE_ACCESS_TOKEN_COOKIE_NAME)
#         if encoded_jws:
#             # TODO: What happens if the token expired while the user was doing payment?
#             # Because the payment flow goes directly from the client to Stripe, it's possible for the
#             # user to sit on the "Proposed Outing" screen for long enough for the access token to expire, and then
#             # click "Book", which sends them to Stripe, which then does the payment stuff and redirects the user back
#             # to our callback URL (this endpoint).
#             # If the access token is expired, which can easily happen, this validation will fail, and the client is
#             # the only app that has the refresh token, and therefore the only app capable of refreshing the access token.
#             # One possible solution is to instead redirect the user from Stripe->Web, and the Web app can then make
#             # follow-up calls to the Core API (during which it will be able to handle token refresh if necessary) to
#             # create the booking, payment references, etc.
#             jws = validate_jws_or_exception(
#                 encoded_jws=encoded_jws,
#                 expected_audience=JWT_AUDIENCE,
#                 expected_issuer=JWT_ISSUER,
#                 expected_purpose=JWTPurpose.ACCESS,
#             )

#             authenticated_account_id = UUID(jws.payload.sub)
#             print(authenticated_account_id)
#         else:
#             raise UnauthorizedError()

#         # payment_intent = request.query_params.get("payment_intent")
#         # payment_intent_client_secret = request.query_params.get("payment_intent_client_secret")
#         # redirect_status = request.query_params.get("redirect_status")
#         # Additional query parameters can also be passed with the `return_url`, which will be persisted

#         # TODO: Update database with payment intent information
#         return RedirectResponse(
#             url=f"{SHARED_CONFIG.eave_dashboard_base_url_public}/booking-confirmation?bookingId=TKTKTK"
#         )
