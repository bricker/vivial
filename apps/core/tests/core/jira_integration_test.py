import http

from eave.core.internal.orm.team import TeamOrm
from eave.core.internal.orm.jira_installation import JiraInstallationOrm
from eave.stdlib.core_api.models.jira import RegisterJiraInstallationInput
from eave.stdlib.core_api.operations.jira import QueryJiraIntegrationRequest, RegisterJiraIntegrationRequest
from eave.stdlib.util import unwrap
from .base import BaseTestCase


class RegisterJiraIntegrationTests(BaseTestCase):
    async def asyncSetUp(self) -> None:
        await super().asyncSetUp()

    async def test_register_new_jira_integration(self) -> None:
        response = await self.make_request(
            path="/integrations/jira/register",
            payload={
                "jira_integration": {
                    "client_key": self.anystring("client_key"),
                    "base_url": self.anystring("base_url"),
                    "atlassian_actor_account_id": self.anystring("atlassian_actor_account_id"),
                    "shared_secret": self.anystring("shared_secret"),
                    "display_url": self.anystring("display_url"),
                    "description": self.anystring("description"),
                },
            },
        )

        assert response.status_code == http.HTTPStatus.OK
        obj = RegisterJiraIntegrationRequest.ResponseBody(**response.json())
        assert obj.jira_integration.client_key == self.getstr("client_key")

        assert self.logged_event(
            event_name="eave_application_integration",
            eave_account_id=None,
            eave_visitor_id=None,
            eave_team_id=None,
            opaque_params={
                "integration_name": "jira",
            }
        )

        async with self.db_session.begin() as s:
            install = await JiraInstallationOrm.one_or_none(
                session=s,
                client_key=self.getstr("client_key"),
            )
            assert install is not None
            assert install.client_key == self.getstr("client_key")
            assert install.base_url == self.getstr("base_url")
            assert install.atlassian_actor_account_id == self.getstr("atlassian_actor_account_id")
            assert install.shared_secret == self.getstr("shared_secret")
            assert install.display_url == self.getstr("display_url")
            assert install.description == self.getstr("description")

    async def test_register_with_existing_jira_integration(self) -> None:
        async with self.db_session.begin() as s:
            await JiraInstallationOrm.create(
                session=s,
                input=RegisterJiraInstallationInput.parse_obj({
                    "client_key":self.anystring("client_key"),
                    "shared_secret":self.anystring("shared_secret"),
                    "base_url":self.anystring("base_url"),
                })
            )

        response = await self.make_request(
            path="/integrations/jira/register",
            payload={
                "jira_integration": {
                    "client_key": self.getstr("client_key"),
                    "base_url": self.getstr("base_url"),
                    "shared_secret": self.getstr("shared_secret"),
                    "atlassian_actor_account_id": self.anystring("atlassian_actor_account_id"),
                    "display_url": self.anystring("display_url"),
                    "description": self.anystring("description"),
                },
            },
        )

        assert response.status_code == http.HTTPStatus.OK
        obj = RegisterJiraIntegrationRequest.ResponseBody(**response.json())
        assert obj.jira_integration.client_key == self.getstr("client_key")

        assert self.logged_event(
            event_name="eave_application_integration_updated",
            eave_account_id=None,
            eave_visitor_id=None,
            eave_team_id=None,
            opaque_params={
                "integration_name": "jira",
            }
        )

        async with self.db_session.begin() as s:
            install2 = await JiraInstallationOrm.one_or_none(
                session=s,
                client_key=self.getstr("client_key"),
            )
            assert install2 is not None
            assert install2.client_key == self.getstr("client_key")
            assert install2.base_url == self.getstr("base_url")
            assert install2.atlassian_actor_account_id == self.getstr("atlassian_actor_account_id")
            assert install2.shared_secret == self.getstr("shared_secret")
            assert install2.display_url == self.getstr("display_url")
            assert install2.description == self.getstr("description")


    async def test_update_existing_jira_integration(self) -> None:
        async with self.db_session.begin() as s:
            await JiraInstallationOrm.create(
                session=s,
                input=RegisterJiraInstallationInput(
                    client_key=self.anystring("client_key"),
                    shared_secret=self.anystring("shared_secret"),
                    base_url=self.anystring("base_url"),
                    atlassian_actor_account_id=self.anystring("atlassian_actor_account_id"),
                    display_url=self.anystring("display_url"),
                    description=self.anystring("description"),

                )
            )

        response = await self.make_request(
            path="/integrations/jira/register",
            payload={
                "jira_integration": {
                    "client_key": self.getstr("client_key"),
                    "base_url": self.anystring("updated base_url"),
                    "shared_secret": self.anystring("updated shared_secret"),
                    "atlassian_actor_account_id": self.anystring("updated atlassian_actor_account_id"),
                },
            },
        )

        assert response.status_code == http.HTTPStatus.OK
        obj = RegisterJiraIntegrationRequest.ResponseBody(**response.json())
        assert obj.jira_integration.client_key == self.getstr("client_key")

        assert self.logged_event(
            event_name="eave_application_integration_updated",
            eave_account_id=None,
            eave_visitor_id=None,
            eave_team_id=None,
            opaque_params={
                "integration_name": "jira",
                "fields_given": ["atlassian_actor_account_id", "base_url", "client_key", "shared_secret"],
            }
        )

        async with self.db_session.begin() as s:
            install = await JiraInstallationOrm.one_or_none(
                session=s,
                client_key=self.getstr("client_key"),
            )
            assert install is not None
            assert install.client_key == self.getstr("client_key")
            assert install.base_url == self.getstr("updated base_url")
            assert install.atlassian_actor_account_id == self.getstr("updated atlassian_actor_account_id")
            assert install.shared_secret == self.getstr("updated shared_secret")
            assert install.display_url == self.getstr("display_url") # test not updated
            assert install.description == self.getstr("description") # test not updated

    async def test_update_existing_jira_integration_with_team(self) -> None:
        async with self.db_session.begin() as s:
            team = await self.make_team(s)

            await JiraInstallationOrm.create(
                session=s,
                team_id=team.id,
                # parse_obj is used here to allow initialization with unset properties
                input=RegisterJiraInstallationInput.parse_obj({
                    "client_key":self.anystring("client_key"),
                    "shared_secret":self.anystring("shared_secret"),
                    "base_url":self.anystring("base_url"),
                })
            )

        response = await self.make_request(
            path="/integrations/jira/register",
            payload={
                "jira_integration": {
                    "client_key": self.getstr("client_key"),
                    "base_url": self.getstr("base_url"),
                    "shared_secret": self.getstr("shared_secret"),
                },
            },
        )

        assert response.status_code == http.HTTPStatus.OK
        obj = RegisterJiraIntegrationRequest.ResponseBody(**response.json())
        assert obj.jira_integration.client_key == self.getstr("client_key")
        assert obj.jira_integration.display_url is None # Not really part of this test case, just checking that this property can be None in this scenario
        assert obj.team is not None
        assert obj.team.id == team.id

        assert self.logged_event(
            event_name="eave_application_integration_updated",
            eave_team_id=team.id,
        )

class QueryJiraIntegrationTests(BaseTestCase):
    async def test_query_when_integration_exists(self) -> None:
        async with self.db_session.begin() as s:
            await JiraInstallationOrm.create(
                session=s,
                # parse_obj is used here to allow initialization with unset properties
                input=RegisterJiraInstallationInput.parse_obj({
                    "client_key":self.anystring("client_key"),
                    "shared_secret":self.anystring("shared_secret"),
                    "base_url":self.anystring("base_url"),
                })
            )

        response = await self.make_request(
            path="/integrations/jira/query",
            payload={
                "jira_integration": {
                    "client_key": self.getstr("client_key"),
                },
            },
        )

        assert response.status_code == http.HTTPStatus.OK
        obj = QueryJiraIntegrationRequest.ResponseBody(**response.json())
        assert obj.jira_integration.client_key == self.getstr("client_key")
        assert obj.team is None

    async def test_query_when_integration_exists_with_team(self) -> None:
        async with self.db_session.begin() as s:
            team = await self.make_team(s)
            await JiraInstallationOrm.create(
                session=s,
                team_id=team.id,
                # parse_obj is used here to allow initialization with unset properties
                input=RegisterJiraInstallationInput.parse_obj({
                    "client_key":self.anystring("client_key"),
                    "shared_secret":self.anystring("shared_secret"),
                    "base_url":self.anystring("base_url"),
                })
            )

        response = await self.make_request(
            path="/integrations/jira/query",
            payload={
                "jira_integration": {
                    "client_key": self.getstr("client_key"),
                },
            },
        )

        assert response.status_code == http.HTTPStatus.OK
        obj = QueryJiraIntegrationRequest.ResponseBody(**response.json())
        assert obj.jira_integration.client_key == self.getstr("client_key")
        assert obj.team is not None
        assert obj.team.id == team.id

    async def test_query_when_integration_doesnt_exist(self) -> None:
        response = await self.make_request(
            path="/integrations/jira/query",
            payload={
                "jira_integration": {
                    "client_key": self.anystring("client_key"),
                },
            },
        )

        assert response.status_code == http.HTTPStatus.NOT_FOUND
        assert response.text == ""

class JiraIntegrationModelTests(BaseTestCase):
    async def asyncSetUp(self) -> None:
        await super().asyncSetUp()
        async with self.db_session.begin() as s:
            team = await self.make_team(s)
            self._data_integration = await JiraInstallationOrm.create(
                session=s,
                team_id=team.id,
                input=RegisterJiraInstallationInput(
                    client_key=self.anystring("client_key"),
                    shared_secret=self.anystring("shared_secret"),
                    base_url=self.anystring("base_url"),
                    atlassian_actor_account_id=self.anystring("atlassian_actor_account_id"),
                    description=self.anystring("description"),
                    display_url=self.anystring("display_url")
                ),
            )

    async def test_update(self) -> None:
        async with self.db_session.begin() as s:
            self._data_integration.update(
                session=s,
                input=RegisterJiraInstallationInput.parse_obj({
                    "client_key": self.getstr("client_key"),
                    "base_url": self.getstr("base_url"),
                    "shared_secret": self.anystring("updated shared_secret")
                })
            )

            assert self._data_integration.shared_secret == self.getstr("updated shared_secret")
            assert self._data_integration.base_url == self.getstr("base_url")
            assert self._data_integration.atlassian_actor_account_id == self.getstr("atlassian_actor_account_id")
            assert self._data_integration.display_url == self.getstr("display_url")
            assert self._data_integration.description == self.getstr("description")

    async def test_update_with_empty_fields(self) -> None:
        async with self.db_session.begin() as s:
            self._data_integration.update(
                session=s,
                input=RegisterJiraInstallationInput.parse_obj({
                    "client_key": self.getstr("client_key"),
                    "shared_secret": "",
                    "base_url": "",
                    "display_url": None,
                })
            )

            assert self._data_integration.shared_secret == self.getstr("shared_secret")
            assert self._data_integration.base_url == self.getstr("base_url")
            assert self._data_integration.display_url is None

    async def test_update_doesnt_update_client_key(self) -> None:
        async with self.db_session.begin() as s:
            self._data_integration.update(
                session=s,
                input=RegisterJiraInstallationInput.parse_obj({
                    # TODO: It's a little awkward to pass `client_key` into this function, knowing it's not used.
                    # Maybe this function should accept a different object, eg `UpdateJiraInstallationInput`
                    "client_key": self.anystring("updated client_key"),
                    "shared_secret": self.getstr("shared_secret"),
                    "base_url": self.getstr("base_url"),
                })
            )

            assert self._data_integration.client_key == self.getstr("client_key")

    async def test_query_with_client_key(self) -> None:
        async with self.db_session.begin() as s:
            result = await JiraInstallationOrm.one_or_none(session=s, client_key=self._data_integration.client_key)
            assert result is not None
            assert result.id == self._data_integration.id

    async def test_query_with_team_id(self) -> None:
        async with self.db_session.begin() as s:
            result = await JiraInstallationOrm.one_or_none(session=s, team_id=unwrap(self._data_integration.team_id))
            assert result is not None
            assert result.id == self._data_integration.id

    async def test_query_with_team_id_and_client_key(self) -> None:
        async with self.db_session.begin() as s:
            result = await JiraInstallationOrm.one_or_none(session=s, team_id=unwrap(self._data_integration.team_id), client_key=self._data_integration.client_key)
            assert result is not None
            assert result.id == self._data_integration.id