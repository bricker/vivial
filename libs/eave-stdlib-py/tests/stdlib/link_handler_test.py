import eave.stdlib.core_api.models as eave_models
import eave.stdlib.core_api.enums as eave_enums
import eave.stdlib.eave_origins as eave_origins
import eave.stdlib.link_handler as link_handler
import eave.stdlib.github_api.client as gh_client
import eave.stdlib.github_api.operations as gh_ops
import eave.stdlib.lib.requests
import mockito
from eave.stdlib.core_api.enums import LinkType
from pydantic import UUID4

from .base import BaseTestCase, mock_coroutine

# set a core_api client origin to make tests not crash from it being unset
eave.stdlib.lib.requests.set_origin(eave_origins.EaveOrigin.eave_slack_app)


class TestLinkHandler(BaseTestCase):
    async def asyncTearDown(self) -> None:
        await super().asyncTearDown()
        mockito.unstub()

    def test_filter_supported_links(self) -> None:
        test_cases = [
            ("https://github.com", [LinkType.github]),
            ("https://github.enterprise.com", [LinkType.github]),
            ("https://github.com/eave-fyi/eave-monorepo/blob/main/.gitignore", [LinkType.github]),
            ("http://github.enterprise.com/the-org/repo-name/path/to/file.txt", [LinkType.github]),
            ("https://api.github.com", []),
            ("https://githubby.com", []),
            ("https://google.com", []),
        ]

        for input_link, expected_result in test_cases:
            result = link_handler.filter_supported_links([input_link])
            assert result == [(input_link, supported) for supported in expected_result]

    async def test_map_link_content(self) -> None:
        # self.setup_shared_mocks()
        dummy_content = gh_ops.GetGithubUrlContent.ResponseBody(content="dummy gh content")
        mockito.when2(gh_client.get_file_content, *mockito.args).thenReturn(mock_coroutine(dummy_content)).thenReturn(
            mock_coroutine(dummy_content)
        )

        dummy_id = UUID4("7b1b3e6a-5a28-4e14-9cad-4a3cbebeee2c")
        input_links = [
            ("https://github.com/eave-fyi/eave-monorepo/blob/main/.gitignore", LinkType.github),
            ("http://github.enterprise.com/the-org/repo-name/path/to/file.txt", LinkType.github),
        ]
        actual_result = await link_handler.map_url_content(
            eave_team_id=dummy_id,
            urls=input_links,
        )

        expected_result = [
            "dummy gh content",
            "dummy gh content",
        ]
        assert actual_result == expected_result
        mockito.verifyStubbedInvocationsAreUsed()

    async def test_subscribe_successful_subscription(self) -> None:
        # self.setup_shared_mocks()
        dummy_id = UUID4("7b1b3e6a-5a28-4e14-9cad-4a3cbebeee2c")
        mockito.when2(gh_client.create_subscription, **mockito.kwargs).thenReturn(
            mock_coroutine(
                gh_ops.CreateGithubResourceSubscription.ResponseBody(
                    subscription=eave_models.Subscription(
                        id=dummy_id,
                        document_reference_id=dummy_id,
                        source=eave_models.SubscriptionSource(
                            platform=eave_enums.SubscriptionSourcePlatform.github,
                            event=eave_enums.SubscriptionSourceEvent.github_file_change,
                            id="id",
                        ),
                    )
                )
            )
        )

        input_links = [
            ("https://github.com/eave-fyi/eave-monorepo/blob/main/.gitignore", LinkType.github),
            ("http://github.enterprise.com/the-org/repo-name/path/to/file.txt", LinkType.github),
        ]
        await link_handler.subscribe_to_file_changes(
            eave_team_id=dummy_id,
            urls=input_links,
        )

        mockito.verifyStubbedInvocationsAreUsed()

    async def test_subscribe_skip_subscription(self) -> None:
        # self.setup_shared_mocks()
        dummy_id = UUID4("7b1b3e6a-5a28-4e14-9cad-4a3cbebeee2c")
        mockito.when2(gh_client.create_subscription, **mockito.kwargs).thenReturn(
            mock_coroutine(
                gh_ops.CreateGithubResourceSubscription.ResponseBody(
                    subscription=eave_models.Subscription(
                        id=dummy_id,
                        document_reference_id=dummy_id,
                        source=eave_models.SubscriptionSource(
                            platform=eave_enums.SubscriptionSourcePlatform.github,
                            event=eave_enums.SubscriptionSourceEvent.github_file_change,
                            id="id",
                        ),
                    )
                )
            )
        )

        # when links don't point to actual files in repo,
        # subscription parsing fails, causing subscription to exit early
        input_links = [
            ("https://github.com/eave-fyi/", LinkType.github),
            ("http://github.enterprise.com/the-org/repo-name/", LinkType.github),
        ]
        await link_handler.subscribe_to_file_changes(
            eave_team_id=dummy_id,
            urls=input_links,
        )

        mockito.verifyStubbedInvocationsAreUsed()

    # def setup_shared_mocks(self) -> None:
    #     dummy_id = UUID4("7b1b3e6a-5a28-4e14-9cad-4a3cbebeee2c")
    #     mockito.when2(eave_core.get_team, **mockito.KWARGS).thenReturn(
    #         mock_coroutine(
    #             eave_ops.GetAuthenticatedAccountTeamIntegrations.ResponseBody(
    #                 account=eave_models.AuthenticatedAccount(
    #                     id=dummy_id,
    #                     auth_provider=enums.AuthProvider.google,
    #                     access_token="dummy token",
    #                     visitor_id=None,
    #                     team_id=dummy_id,
    #                 ),
    #                 team=eave_models.Team(
    #                     id=dummy_id,
    #                     name="Team name",
    #                     document_platform=enums.DocumentPlatform.confluence,
    #                 ),
    #                 integrations=eave_models.Integrations(
    #                     github=eave_models.GithubInstallation(
    #                         id=dummy_id,
    #                         team_id=dummy_id,
    #                         github_install_id="install id",
    #                     ),
    #                     slack=None,
    #                     atlassian=None,
    #                 ),
    #             )
    #         )
    #     )
