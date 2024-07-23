import uuid
from typing import Unpack

from aiohttp.hdrs import METH_POST

from eave.stdlib.core_api.models.onboarding_submissions import OnboardingSubmission
from eave.stdlib.core_api.models.team import Team
from eave.stdlib.endpoints import BaseRequestBody, BaseResponseBody

from ... import requests_util
from . import CoreApiEndpoint, CoreApiEndpointConfiguration


class GetMyOnboardingSubmissionRequest(CoreApiEndpoint):
    config = CoreApiEndpointConfiguration(
        path="/public/me/onboarding-submissions/query",
        method=METH_POST,
        auth_required=True,
        origin_required=True,
        is_public=True,
    )

    class ResponseBody(BaseResponseBody):
        onboarding_submission: OnboardingSubmission
        team: Team

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


class CreateMyOnboardingSubmissionRequest(CoreApiEndpoint):
    config = CoreApiEndpointConfiguration(
        path="/public/me/onboarding-submissions/create",
        method=METH_POST,
        auth_required=True,
        origin_required=True,
        is_public=True,
    )

    class RequestBody(BaseRequestBody):
        form_data: dict[str, list[str]]

    class ResponseBody(BaseResponseBody):
        onboarding_submission: OnboardingSubmission
        team: Team

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
