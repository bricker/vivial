from http import HTTPStatus

import aiohttp
from tests.core.bq_tests_base import BigQueryTestsBase

from eave.collectors.core.datastructures import DataIngestRequestBody, LogIngestRequestBody
from eave.core.internal.orm.client_credentials import ClientCredentialsOrm, ClientScope
from eave.stdlib.headers import EAVE_CLIENT_ID_HEADER, EAVE_CLIENT_SECRET_HEADER


class TestClientCredentialsFromHeadersMiddleware(BigQueryTestsBase):
    async def test_invalid_client_headers_is_unauthorized(self) -> None:
        response = await self.make_request(
            path="/public/ingest/server",
            headers={
                EAVE_CLIENT_ID_HEADER: str(self.anyuuid("invalid client ID")),
                EAVE_CLIENT_SECRET_HEADER: self.anystr("invalid client secret"),
            },
            payload=DataIngestRequestBody(events={}).to_dict(),
        )

        assert response.status_code == HTTPStatus.UNAUTHORIZED

    async def test_valid_client_headers_ok(self) -> None:
        response = await self.make_request(
            path="/public/ingest/server",
            headers={
                EAVE_CLIENT_ID_HEADER: str(self.client_credentials.id),
                EAVE_CLIENT_SECRET_HEADER: self.client_credentials.secret,
            },
            payload=DataIngestRequestBody(events={}).to_dict(),
        )

        assert response.status_code == HTTPStatus.OK

    async def test_valid_client_headers_without_write_scope_forbidden(self) -> None:
        async with self.db_session.begin() as s:
            ro_creds = await ClientCredentialsOrm.create(
                session=s,
                team_id=self.eave_team.id,
                description=self.anystr(),
                scope=ClientScope.read,
            )

        response = await self.make_request(
            path="/public/ingest/server",
            headers={
                EAVE_CLIENT_ID_HEADER: str(ro_creds.id),
                EAVE_CLIENT_SECRET_HEADER: ro_creds.secret,
            },
            payload=DataIngestRequestBody(events={}).to_dict(),
        )

        assert response.status_code == HTTPStatus.FORBIDDEN

    async def test_client_qp_unauthorized(self) -> None:
        response = await self.make_request(
            path="/public/ingest/server?clientId={self.client_credentials.id}",
            headers={
                aiohttp.hdrs.ORIGIN: "https://eave.test",
            },
            payload=DataIngestRequestBody(events={}).to_dict(),
        )

        assert response.status_code == HTTPStatus.BAD_REQUEST


class TestClientCredentialsFromQueryParamsMiddleware(BigQueryTestsBase):
    async def test_invalid_client_qp_is_unauthorized(self) -> None:
        response = await self.make_request(
            path=f"/public/ingest/browser?clientId={self.anyuuid("invalid client ID")}",
            headers={
                aiohttp.hdrs.ORIGIN: "https://eave.test",
            },
            payload=DataIngestRequestBody(events={}).to_dict(),
        )

        assert response.status_code == HTTPStatus.UNAUTHORIZED

    async def test_valid_client_qp_ok(self) -> None:
        response = await self.make_request(
            path=f"/public/ingest/browser?clientId={self.client_credentials.id}",
            headers={
                aiohttp.hdrs.ORIGIN: "https://eave.test",
            },
            payload=DataIngestRequestBody(events={}).to_dict(),
        )

        assert response.status_code == HTTPStatus.OK

    async def test_valid_client_qp_without_write_scope_forbidden(self) -> None:
        async with self.db_session.begin() as s:
            ro_creds = await ClientCredentialsOrm.create(
                session=s,
                team_id=self.eave_team.id,
                description=self.anystr(),
                scope=ClientScope.read,
            )

        response = await self.make_request(
            path=f"/public/ingest/browser?clientId={ro_creds.id}",
            headers={
                aiohttp.hdrs.ORIGIN: "https://eave.test",
            },
            payload=DataIngestRequestBody(events={}).to_dict(),
        )

        assert response.status_code == HTTPStatus.FORBIDDEN

    async def test_client_headers_unauthorized(self) -> None:
        response = await self.make_request(
            path="/public/ingest/browser",
            headers={
                EAVE_CLIENT_ID_HEADER: str(self.client_credentials.id),
                EAVE_CLIENT_SECRET_HEADER: self.client_credentials.secret,
            },
            payload=DataIngestRequestBody(events={}).to_dict(),
        )

        assert response.status_code == HTTPStatus.BAD_REQUEST


class TestClientCredentialsFromHeadersOrQueryParamsMiddleware(BigQueryTestsBase):
    async def test_invalid_client_qp_is_unauthorized(self) -> None:
        response = await self.make_request(
            path=f"/public/ingest/log?clientId={self.anyuuid("invalid client ID")}",
            headers={
                aiohttp.hdrs.ORIGIN: "https://eave.test",
            },
            payload=LogIngestRequestBody(logs=[]).to_dict(),
        )

        assert response.status_code == HTTPStatus.UNAUTHORIZED

    async def test_invalid_client_headers_is_unauthorized(self) -> None:
        response = await self.make_request(
            path="/public/ingest/log",
            headers={
                EAVE_CLIENT_ID_HEADER: str(self.anyuuid("invalid client ID")),
                EAVE_CLIENT_SECRET_HEADER: self.anystr("invalid client secret"),
            },
            payload=LogIngestRequestBody(logs=[]).to_dict(),
        )

        assert response.status_code == HTTPStatus.UNAUTHORIZED

    async def test_valid_client_qp_ok(self) -> None:
        response = await self.make_request(
            path=f"/public/ingest/log?clientId={self.client_credentials.id}",
            headers={
                aiohttp.hdrs.ORIGIN: "https://eave.test",
            },
            payload=LogIngestRequestBody(logs=[]).to_dict(),
        )

        assert response.status_code == HTTPStatus.OK

    async def test_valid_client_headers_ok(self) -> None:
        response = await self.make_request(
            path="/public/ingest/log",
            headers={
                EAVE_CLIENT_ID_HEADER: str(self.client_credentials.id),
                EAVE_CLIENT_SECRET_HEADER: self.client_credentials.secret,
            },
            payload=LogIngestRequestBody(logs=[]).to_dict(),
        )

        assert response.status_code == HTTPStatus.OK

    async def test_valid_client_headers_without_write_scope_forbidden(self) -> None:
        async with self.db_session.begin() as s:
            ro_creds = await ClientCredentialsOrm.create(
                session=s,
                team_id=self.eave_team.id,
                description=self.anystr(),
                scope=ClientScope.read,
            )

        response = await self.make_request(
            path="/public/ingest/log",
            headers={
                EAVE_CLIENT_ID_HEADER: str(ro_creds.id),
                EAVE_CLIENT_SECRET_HEADER: ro_creds.secret,
            },
            payload=LogIngestRequestBody(logs=[]).to_dict(),
        )

        assert response.status_code == HTTPStatus.FORBIDDEN

    async def test_valid_client_qp_without_write_scope_forbidden(self) -> None:
        async with self.db_session.begin() as s:
            ro_creds = await ClientCredentialsOrm.create(
                session=s,
                team_id=self.eave_team.id,
                description=self.anystr(),
                scope=ClientScope.read,
            )

        response = await self.make_request(
            path=f"/public/ingest/log?clientId={ro_creds.id}",
            headers={
                aiohttp.hdrs.ORIGIN: "https://eave.test",
            },
            payload=LogIngestRequestBody(logs=[]).to_dict(),
        )

        assert response.status_code == HTTPStatus.FORBIDDEN
