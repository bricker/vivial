from aiohttp.hdrs import METH_POST
from eave.stdlib.core_api.operations import CoreApiEndpoint, CoreApiEndpointConfiguration


class LoginRequest(CoreApiEndpoint):
    config = CoreApiEndpointConfiguration(
        path="/public/auth/login",
        method=METH_POST,
        auth_required=True,
        origin_required=True,
        is_public=True,
    )

    class ResponseBody(BaseResponseBody):
        account: AuthenticatedAccount

    @classmethod
    async def perform(
        cls,
        *,
        account_id: uuid.UUID | str,
        access_token: str,
        **kwargs: Unpack[requests_util.CommonRequestArgs],
    ) -> ResponseBody:
        response = await requests_util.make_request(
            config=cls.config,
            input=None,
            access_token=access_token,
            account_id=account_id,
            **kwargs,
        )

        body = await cls.make_response(response, cls.ResponseBody)
        return body
