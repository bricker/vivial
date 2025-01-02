from http import HTTPStatus
from typing import Any, override
from uuid import UUID

from httpx import Response
from strawberry.types import ExecutionResult

from eave.core.auth_cookies import ACCESS_TOKEN_COOKIE_NAME
from eave.core.config import JWT_AUDIENCE, JWT_ISSUER
from eave.dev_tooling.constants import EAVE_HOME
from eave.stdlib.jwt import JWTPurpose, create_jws
from eave.stdlib.test_helpers.random_data_mixin import RandomDataMixin
from eave.stdlib.time import ONE_YEAR_IN_MINUTES

from .http_client_mixin import HTTPClientMixin


class GraphQLMixin(RandomDataMixin, HTTPClientMixin):
    _gql_cache: dict[str, str]  # pyright: ignore [reportUninitializedInstanceVariable]

    @override
    async def asyncSetUp(self) -> None:
        await super().asyncSetUp()
        self._gql_cache = {}

    def load_graphql_query(self, name: str) -> str:
        if name not in self._gql_cache:
            with open(f"{EAVE_HOME}/apps/core/tests/core/resolvers/graphql/{name}.graphql") as f:
                self._gql_cache[name] = f.read()

        return self._gql_cache[name]

    def parse_graphql_response(self, response: Response) -> ExecutionResult:
        j = response.json()

        result = ExecutionResult(
            data=j.get("data"),
            errors=j.get("errors"),
        )

        return result

    async def make_graphql_request(
        self,
        query_name: str,
        variables: dict[str, Any],
        *,
        account_id: UUID | None = None,
        cookies: dict[str, str] | None = None,
    ) -> Response:
        if cookies is None:
            cookies = {}

        if account_id and ACCESS_TOKEN_COOKIE_NAME not in cookies:
            jws = create_jws(
                purpose=JWTPurpose.ACCESS,
                issuer=JWT_ISSUER,
                audience=JWT_AUDIENCE,
                subject=str(account_id),
                jwt_id=self.anystr(),
                max_age_minutes=ONE_YEAR_IN_MINUTES,
            )

            cookies[ACCESS_TOKEN_COOKIE_NAME] = jws

        response = await self.httpclient.post(
            "/graphql",
            json={
                "query": self.load_graphql_query(query_name),
                "variables": variables,
            },
            cookies=cookies,
        )

        assert response.status_code == HTTPStatus.OK
        return response
