import http

from eave.core.internal.orm.connect_installation import ConnectInstallationOrm
from eave.stdlib.core_api.models.connect import AtlassianProduct, RegisterConnectInstallationInput
from eave.stdlib.core_api.operations.connect import QueryConnectIntegrationRequest, RegisterConnectIntegrationRequest
from eave.stdlib.util import unwrap
from .base import BaseTestCase


class RegisterConnectIntegrationTests(BaseTestCase):
    async def asyncSetUp(self) -> None:
        await super().asyncSetUp()

    async def test_register_new_connect_integration(self) -> None:
        response = await self.make_request(
            path="/integrations/connect/register",
            payload={
                "connect_integration": {
                    "product": "confluence",
                    "client_key": self.anystring("client_key"),
                    "base_url": self.anyurl("base_url"),
                    "atlassian_actor_account_id": self.anystring("atlassian_actor_account_id"),
                    "shared_secret": self.anystring("shared_secret"),
                    "display_url": self.anystring("display_url"),
                    "description": self.anystring("description"),
                },
            },
        )

        assert response.status_code == http.HTTPStatus.OK
        obj = RegisterConnectIntegrationRequest.ResponseBody(**response.json())
        assert obj.connect_integration.client_key == self.getstr("client_key")

        assert self.logged_event(
            event_name="eave_connect_app_registered",
            eave_account_id=None,
            eave_visitor_id=None,
            eave_team_id=None,
            opaque_params={
                "integration_name": "confluence",
            },
        )

        async with self.db_session.begin() as s:
            install = await ConnectInstallationOrm.one_or_none(
                session=s,
                product=AtlassianProduct.confluence,
                client_key=self.getstr("client_key"),
            )
            assert install is not None
            assert install.product == AtlassianProduct.confluence
            assert install.client_key == self.getstr("client_key")
            assert install.base_url == self.geturl("base_url")
            assert install.atlassian_actor_account_id == self.getstr("atlassian_actor_account_id")
            assert install.shared_secret == self.getstr("shared_secret")
            assert install.display_url == self.getstr("display_url")
            assert install.description == self.getstr("description")

    async def test_register_with_existing_connect_integration(self) -> None:
        async with self.db_session.begin() as s:
            await ConnectInstallationOrm.create(
                session=s,
                product=AtlassianProduct.jira,
                client_key=self.anystring("client_key"),
                shared_secret=self.anystring("shared_secret"),
                base_url=self.anyurl("base_url"),
            )

        response = await self.make_request(
            path="/integrations/connect/register",
            payload={
                "connect_integration": {
                    "product": "jira",
                    "client_key": self.getstr("client_key"),
                    "base_url": self.geturl("base_url"),
                    "shared_secret": self.getstr("shared_secret"),
                    "atlassian_actor_account_id": self.anystring("atlassian_actor_account_id"),
                    "display_url": self.anystring("display_url"),
                    "description": self.anystring("description"),
                },
            },
        )

        assert response.status_code == http.HTTPStatus.OK
        obj = RegisterConnectIntegrationRequest.ResponseBody(**response.json())
        assert obj.connect_integration.client_key == self.getstr("client_key")

        assert self.logged_event(
            event_name="eave_application_integration_updated",
            eave_account_id=None,
            eave_visitor_id=None,
            eave_team_id=None,
            opaque_params={
                "integration_name": "jira",
            },
        )

        async with self.db_session.begin() as s:
            install2 = await ConnectInstallationOrm.one_or_none(
                session=s,
                product=AtlassianProduct.jira,
                client_key=self.getstr("client_key"),
            )
            assert install2 is not None
            assert install2.product == "jira"
            assert install2.client_key == self.getstr("client_key")
            assert install2.base_url == self.geturl("base_url")
            assert install2.atlassian_actor_account_id == self.getstr("atlassian_actor_account_id")
            assert install2.shared_secret == self.getstr("shared_secret")
            assert install2.display_url == self.getstr("display_url")
            assert install2.description == self.getstr("description")

    async def test_update_existing_connect_integration(self) -> None:
        async with self.db_session.begin() as s:
            await ConnectInstallationOrm.create(
                session=s,
                product=AtlassianProduct.jira,
                client_key=self.anystring("client_key"),
                shared_secret=self.anystring("shared_secret"),
                base_url=self.anyurl("base_url"),
                atlassian_actor_account_id=self.anystring("atlassian_actor_account_id"),
                display_url=self.anystring("display_url"),
                description=self.anystring("description"),
            )

        response = await self.make_request(
            path="/integrations/connect/register",
            payload={
                "connect_integration": {
                    "product": "jira",
                    "client_key": self.getstr("client_key"),
                    "base_url": self.anystring("updated base_url"),
                    "shared_secret": self.anystring("updated shared_secret"),
                    "atlassian_actor_account_id": self.anystring("updated atlassian_actor_account_id"),
                },
            },
        )

        assert response.status_code == http.HTTPStatus.OK
        obj = RegisterConnectIntegrationRequest.ResponseBody(**response.json())
        assert obj.connect_integration.client_key == self.getstr("client_key")

        assert self.logged_event(
            event_name="eave_application_integration_updated",
            eave_account_id=None,
            eave_visitor_id=None,
            eave_team_id=None,
            opaque_params={
                "integration_name": "jira",
            },
        )

        async with self.db_session.begin() as s:
            install = await ConnectInstallationOrm.one_or_none(
                session=s,
                product=AtlassianProduct.jira,
                client_key=self.getstr("client_key"),
            )
            assert install is not None
            assert install.product == "jira"
            assert install.client_key == self.getstr("client_key")
            assert install.base_url == self.getstr("updated base_url")
            assert install.atlassian_actor_account_id == self.getstr("updated atlassian_actor_account_id")
            assert install.shared_secret == self.getstr("updated shared_secret")
            assert install.display_url == self.getstr("display_url")  # test not updated
            assert install.description == self.getstr("description")  # test not updated

    async def test_update_existing_connect_integration_with_team(self) -> None:
        async with self.db_session.begin() as s:
            team = await self.make_team(s)

            await ConnectInstallationOrm.create(
                session=s,
                team_id=team.id,
                product=AtlassianProduct.jira,
                client_key=self.anystring("client_key"),
                shared_secret=self.anystring("shared_secret"),
                base_url=self.anyurl("base_url"),
            )

        response = await self.make_request(
            path="/integrations/connect/register",
            payload={
                "connect_integration": {
                    "product": "jira",
                    "client_key": self.getstr("client_key"),
                    "base_url": self.geturl("base_url"),
                    "shared_secret": self.getstr("shared_secret"),
                },
            },
        )

        assert response.status_code == http.HTTPStatus.OK
        obj = RegisterConnectIntegrationRequest.ResponseBody(**response.json())
        assert obj.connect_integration.client_key == self.getstr("client_key")
        assert (
            obj.connect_integration.display_url is None
        )  # Not really part of this test case, just checking that this property can be None in this scenario
        assert obj.team is not None
        assert obj.team.id == team.id

        assert self.logged_event(
            event_name="eave_application_integration_updated",
            eave_team=team.analytics_model,
        )

    async def test_Register_With_Matching_Connect_App(self) -> None:
        """
        When a new Connect app is registered, the system should look for other existing Connect apps with the same org_url property,
        and use its team ID. The allows, for example, a Jira installation to be automatically linked to the correct Eave team.
        """
        async with self.db_session.begin() as s:
            team = await self.make_team(s)

            await ConnectInstallationOrm.create(
                session=s,
                team_id=team.id,
                product=AtlassianProduct.confluence,
                client_key=self.anystring("confluence client_key"),
                shared_secret=self.anystring("confluence shared_secret"),
                base_url=self.anyurl("base_url") + "/wiki",
            )

        response = await self.make_request(
            path="/integrations/connect/register",
            payload={
                "connect_integration": {
                    "product": "jira",
                    "client_key": self.anystring("jira client_key"),
                    "shared_secret": self.anystring("jira shared_secret"),
                    "base_url": self.geturl("base_url") + "/jira",
                },
            },
        )

        assert response.status_code == http.HTTPStatus.OK
        obj = RegisterConnectIntegrationRequest.ResponseBody(**response.json())
        assert obj.connect_integration.client_key == self.getstr("jira client_key")
        assert obj.connect_integration.shared_secret == self.getstr("jira shared_secret")
        assert obj.team is not None
        assert obj.team.id == team.id

        assert self.logged_event(
            event_name="eave_application_integration",
            eave_team=team.analytics_model,
            opaque_params={
                "integration_name": AtlassianProduct.jira,
            },
        )


class QueryConnectIntegrationTests(BaseTestCase):
    async def test_query_when_integration_exists(self) -> None:
        async with self.db_session.begin() as s:
            await ConnectInstallationOrm.create(
                session=s,
                product=AtlassianProduct.jira,
                client_key=self.anystring("client_key"),
                shared_secret=self.anystring("shared_secret"),
                base_url=self.anyurl("base_url"),
            )

        response = await self.make_request(
            path="/integrations/connect/query",
            payload={
                "connect_integration": {
                    "product": "jira",
                    "client_key": self.getstr("client_key"),
                },
            },
        )

        assert response.status_code == http.HTTPStatus.OK
        obj = QueryConnectIntegrationRequest.ResponseBody(**response.json())
        assert obj.connect_integration.product == "jira"
        assert obj.connect_integration.client_key == self.getstr("client_key")
        assert obj.team is None

    async def test_query_confluence(self) -> None:
        async with self.db_session.begin() as s:
            await ConnectInstallationOrm.create(
                session=s,
                product=AtlassianProduct.confluence,
                client_key=self.anystring("client_key"),
                shared_secret=self.anystring("shared_secret"),
                base_url=self.anyurl("base_url"),
            )

        response = await self.make_request(
            path="/integrations/connect/query",
            payload={
                "connect_integration": {
                    "product": "confluence",
                    "client_key": self.getstr("client_key"),
                },
            },
        )

        assert response.status_code == http.HTTPStatus.OK
        obj = QueryConnectIntegrationRequest.ResponseBody(**response.json())
        assert obj.connect_integration.product == AtlassianProduct.confluence
        assert obj.connect_integration.client_key == self.getstr("client_key")

    async def test_query_with_product(self) -> None:
        async with self.db_session.begin() as s:
            await ConnectInstallationOrm.create(
                session=s,
                product=AtlassianProduct.confluence,
                client_key=self.anystring("client_key"),
                shared_secret=self.anystring("shared_secret"),
                base_url=self.anyurl("base_url"),
            )

        response = await self.make_request(
            path="/integrations/connect/query",
            payload={
                "connect_integration": {
                    "product": "jira",  # This is different from the object created above
                    "client_key": self.getstr("client_key"),
                },
            },
        )

        assert response.status_code == http.HTTPStatus.NOT_FOUND
        assert response.text == ""

    async def test_query_when_integration_exists_with_team(self) -> None:
        async with self.db_session.begin() as s:
            team = await self.make_team(s)
            await ConnectInstallationOrm.create(
                session=s,
                team_id=team.id,
                product=AtlassianProduct.jira,
                client_key=self.anystring("client_key"),
                shared_secret=self.anystring("shared_secret"),
                base_url=self.anyurl("base_url"),
            )

        response = await self.make_request(
            path="/integrations/connect/query",
            payload={
                "connect_integration": {
                    "product": "jira",
                    "client_key": self.getstr("client_key"),
                },
            },
        )

        assert response.status_code == http.HTTPStatus.OK
        obj = QueryConnectIntegrationRequest.ResponseBody(**response.json())
        assert obj.connect_integration.client_key == self.getstr("client_key")
        assert obj.team is not None
        assert obj.team.id == team.id

    async def test_query_with_team_id(self) -> None:
        async with self.db_session.begin() as s:
            team = await self.make_team(s)
            await ConnectInstallationOrm.create(
                session=s,
                team_id=team.id,
                product=AtlassianProduct.jira,
                client_key=self.anystring("client_key"),
                shared_secret=self.anystring("shared_secret"),
                base_url=self.anyurl("base_url"),
            )

        response = await self.make_request(
            path="/integrations/connect/query",
            payload={
                "connect_integration": {
                    "product": "jira",
                    "team_id": str(team.id),
                },
            },
        )

        assert response.status_code == http.HTTPStatus.OK
        obj = QueryConnectIntegrationRequest.ResponseBody(**response.json())
        assert obj.connect_integration.client_key == self.getstr("client_key")
        assert obj.team is not None
        assert obj.team.id == team.id

    async def test_query_with_client_key(self) -> None:
        async with self.db_session.begin() as s:
            team = await self.make_team(s)
            await ConnectInstallationOrm.create(
                session=s,
                team_id=team.id,
                product=AtlassianProduct.jira,
                client_key=self.anystring("client_key"),
                shared_secret=self.anystring("shared_secret"),
                base_url=self.anyurl("base_url"),
            )

        response = await self.make_request(
            path="/integrations/connect/query",
            payload={
                "connect_integration": {
                    "product": "jira",
                    "client_key": self.getstr("client_key"),
                },
            },
        )

        assert response.status_code == http.HTTPStatus.OK
        obj = QueryConnectIntegrationRequest.ResponseBody(**response.json())
        assert obj.connect_integration.client_key == self.getstr("client_key")
        assert obj.team is not None
        assert obj.team.id == team.id

    async def test_query_with_invalid_params(self) -> None:
        async with self.db_session.begin() as s:
            team = await self.make_team(s)
            await ConnectInstallationOrm.create(
                session=s,
                team_id=team.id,
                product=AtlassianProduct.jira,
                client_key=self.anystring("client_key"),
                shared_secret=self.anystring("shared_secret"),
                base_url=self.anyurl("base_url"),
            )

        response = await self.make_request(
            path="/integrations/connect/query",
            payload={
                "connect_integration": {
                    "product": "jira",
                    "client_key": self.getstr("client_key"),
                },
            },
        )

        assert response.status_code == http.HTTPStatus.OK
        obj = QueryConnectIntegrationRequest.ResponseBody(**response.json())
        assert obj.connect_integration.client_key == self.getstr("client_key")
        assert obj.team is not None
        assert obj.team.id == team.id

    async def test_query_when_integration_doesnt_exist(self) -> None:
        response = await self.make_request(
            path="/integrations/connect/query",
            payload={
                "connect_integration": {
                    "product": "jira",
                    "client_key": self.anystring("client_key"),
                },
            },
        )

        assert response.status_code == http.HTTPStatus.NOT_FOUND
        assert response.text == ""


class ConnectIntegrationModelTests(BaseTestCase):
    async def asyncSetUp(self) -> None:
        await super().asyncSetUp()
        async with self.db_session.begin() as s:
            team = await self.make_team(s)
            self._data_integration = await ConnectInstallationOrm.create(
                session=s,
                team_id=team.id,
                product=AtlassianProduct.jira,
                client_key=self.anystring("client_key"),
                shared_secret=self.anystring("shared_secret"),
                base_url=self.anyurl("base_url"),
                atlassian_actor_account_id=self.anystring("atlassian_actor_account_id"),
                description=self.anystring("description"),
                display_url=self.anystring("display_url"),
            )

    async def test_update(self) -> None:
        async with self.db_session.begin() as s:
            self._data_integration.update(
                session=s,
                input=RegisterConnectInstallationInput.parse_obj(
                    {
                        "product": "jira",
                        "client_key": self.getstr("client_key"),
                        "base_url": self.geturl("base_url"),
                        "shared_secret": self.anystring("updated shared_secret"),
                    }
                ),
            )

            assert self._data_integration.shared_secret == self.getstr("updated shared_secret")
            assert self._data_integration.base_url == self.geturl("base_url")
            assert self._data_integration.atlassian_actor_account_id == self.getstr("atlassian_actor_account_id")
            assert self._data_integration.display_url == self.getstr("display_url")
            assert self._data_integration.description == self.getstr("description")

    async def test_update_with_empty_fields(self) -> None:
        async with self.db_session.begin() as s:
            self._data_integration.update(
                session=s,
                input=RegisterConnectInstallationInput.parse_obj(
                    {
                        "product": "jira",
                        "client_key": self.getstr("client_key"),
                        "shared_secret": "",
                        "base_url": "",
                        "display_url": None,
                    }
                ),
            )

            assert self._data_integration.shared_secret == self.getstr("shared_secret")
            assert self._data_integration.base_url == self.geturl("base_url")
            assert self._data_integration.display_url is None

    async def test_update_doesnt_update_client_key(self) -> None:
        async with self.db_session.begin() as s:
            self._data_integration.update(
                session=s,
                input=RegisterConnectInstallationInput.parse_obj(
                    {
                        # TODO: It's a little awkward to pass `client_key` into this function, knowing it's not used.
                        # Maybe this function should accept a different object, eg `UpdateJiraInstallationInput`
                        "product": "jira",
                        "client_key": self.anystring("updated client_key"),
                        "shared_secret": self.getstr("shared_secret"),
                        "base_url": self.geturl("base_url"),
                    }
                ),
            )

            assert self._data_integration.client_key == self.getstr("client_key")

    async def test_update_doesnt_update_product(self) -> None:
        async with self.db_session.begin() as s:
            self._data_integration.update(
                session=s,
                input=RegisterConnectInstallationInput.parse_obj(
                    {
                        # TODO: It's a little awkward to pass `client_key` into this function, knowing it's not used.
                        # Maybe this function should accept a different object, eg `UpdateJiraInstallationInput`
                        "product": "confluence",
                        "client_key": self.getstr("client_key"),
                        "shared_secret": self.getstr("shared_secret"),
                        "base_url": self.geturl("base_url"),
                    }
                ),
            )

            assert self._data_integration.product == AtlassianProduct.jira

    async def test_query_with_product_and_client_key(self) -> None:
        async with self.db_session.begin() as s:
            result = await ConnectInstallationOrm.one_or_none(
                session=s, client_key=self._data_integration.client_key, product=AtlassianProduct.jira
            )
            assert result is not None
            assert result.id == self._data_integration.id

    async def test_query_with_client_key_only(self) -> None:
        async with self.db_session.begin() as s:
            result = await ConnectInstallationOrm.one_or_none(
                session=s, product=AtlassianProduct.jira, client_key=self._data_integration.client_key
            )
            assert result is not None

    async def test_query_with_team_id(self) -> None:
        async with self.db_session.begin() as s:
            result = await ConnectInstallationOrm.one_or_none(
                session=s, product=AtlassianProduct.jira, team_id=unwrap(self._data_integration.team_id)
            )
            assert result is not None
            assert result.id == self._data_integration.id

    async def test_query_with_team_id_but_wrong_product(self) -> None:
        async with self.db_session.begin() as s:
            result = await ConnectInstallationOrm.one_or_none(
                session=s, product=AtlassianProduct.confluence, team_id=unwrap(self._data_integration.team_id)
            )
            assert result is None

    async def test_query_with_team_id_and_client_key(self) -> None:
        async with self.db_session.begin() as s:
            result = await ConnectInstallationOrm.one_or_none(
                session=s,
                team_id=unwrap(self._data_integration.team_id),
                product=AtlassianProduct.jira,
                client_key=self._data_integration.client_key,
            )
            assert result is not None
            assert result.id == self._data_integration.id
