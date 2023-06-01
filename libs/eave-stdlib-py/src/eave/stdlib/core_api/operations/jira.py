from typing import Optional
import uuid
from eave.stdlib.core_api.models import team
from eave.stdlib.core_api.models.jira import JiraInstallation, RegisterJiraInstallationInput

from . import BaseRequestBody, BaseResponseBody, Endpoint, EndpointConfiguration

from eave.stdlib.eave_origins import EaveOrigin

from ... import requests

class RegisterJiraIntegrationRequest(Endpoint):
    config = EndpointConfiguration(
        path="/integrations/jira/register",
        auth_required=False,
        team_id_required=False,
        signature_required=True,
        origin_required=True,
    )

    class RequestBody(BaseRequestBody):
        jira_integration: RegisterJiraInstallationInput

    class ResponseBody(BaseResponseBody):
        team: Optional[team.Team]
        jira_integration: JiraInstallation

    @classmethod
    async def perform(cls,
        origin: EaveOrigin,
        input: RequestBody,
    ) -> ResponseBody:
        response = await requests.make_request(
            url=cls.config.url,
            origin=origin,
            input=input,
        )

        response_json = await response.json()
        return cls.ResponseBody(**response_json)


# class QueryJiraInstallation(Endpoint):
#     config = EndpointConfiguration(
#         path="/integrations/jira/query",
#         auth_required=False,
#         team_id_required=False,
#         signature_required=True,
#         origin_required=True,
#     )

#     class RequestBody(BaseRequestBody):
#         jira_integration: QueryJiraInstallationInput

#     class ResponseBody(BaseResponseBody):
#         team: Optional[team.Team]
#         jira_integration: Optional[JiraInstallation]

#     @classmethod
#     async def perform(cls,
#         origin: EaveOrigin,
#         input: RequestBody,
#     ) -> ResponseBody:
#         response = await requests.make_request(
#             url=cls.config.url,
#             origin=origin,
#             input=input,
#         )

#         response_json = await response.json()
#         return cls.ResponseBody(**response_json)
