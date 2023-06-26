from eave.stdlib.core_api.enums import LinkType
from eave.stdlib.core_api.models.subscriptions import (
    SubscriptionSource,
    SubscriptionSourceEvent,
    SubscriptionSourcePlatform,
)
from eave.stdlib.core_api.models.subscriptions import (
    Subscription,
)
from eave.stdlib.core_api.models.team import DocumentPlatform, Team
from eave.stdlib.core_api.operations.subscriptions import CreateSubscriptionRequest
from eave.stdlib.eave_origins import EaveOrigin
import eave.stdlib.link_handler as link_handler
import eave.stdlib.github_api.operations as gh_ops
from eave.stdlib.test_util import UtilityBaseTestCase
import unittest.mock


class TestLinkHandler(UtilityBaseTestCase):
    async def asyncSetUp(self) -> None:
        await super().asyncSetUp()
        self.patch(
            patch=unittest.mock.patch(
                "eave.stdlib.link_handler.github_api_client.create_subscription",
                return_value=CreateSubscriptionRequest.ResponseBody(
                    team=Team(
                        id=self.anyuuid(),
                        name=self.anystr(),
                        document_platform=DocumentPlatform.confluence,
                    ),
                    subscription=Subscription(
                        id=self.anyuuid(),
                        document_reference_id=self.anyuuid(),
                        source=SubscriptionSource(
                            platform=SubscriptionSourcePlatform.github,
                            event=SubscriptionSourceEvent.github_file_change,
                            id=self.anystring(),
                        ),
                    )
                ),
            ),
        )

        self.patch(
            name="github_client.get_file_content",
            patch=unittest.mock.patch("eave.stdlib.link_handler.github_api_client.get_file_content"),
        )

    async def test_filter_supported_links(self) -> None:
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
        mock = self.get_mock("github_client.get_file_content")
        mock.side_effect = [
            gh_ops.GetGithubUrlContent.ResponseBody(content=self.anystring("file content 1")),
            gh_ops.GetGithubUrlContent.ResponseBody(content=self.anystring("file content 2")),
        ]

        input_links = [
            ("https://github.com/eave-fyi/eave-monorepo/blob/main/.gitignore", LinkType.github),
            ("http://github.enterprise.com/the-org/repo-name/path/to/file.txt", LinkType.github),
        ]
        actual_result = await link_handler.map_url_content(
            origin=EaveOrigin.eave_slack_app,
            eave_team_id=self.anyuuid(),
            urls=input_links,
        )

        expected_result = [
            self.anystring("file content 1"),
            self.anystring("file content 2"),
        ]
        assert actual_result == expected_result

    async def test_subscribe_successful_subscription(self) -> None:
        input_links = [
            ("https://github.com/eave-fyi/eave-monorepo/blob/main/.gitignore", LinkType.github),
            ("http://github.enterprise.com/the-org/repo-name/path/to/file.txt", LinkType.github),
        ]
        subscriptions = await link_handler.subscribe_to_file_changes(
            origin=EaveOrigin.eave_slack_app,
            eave_team_id=self.anyuuid(),
            urls=input_links,
        )
        assert len(subscriptions) == 2
        assert subscriptions[0].subscription and subscriptions[0].subscription.source.platform == SubscriptionSourcePlatform.github
        assert subscriptions[1].subscription and subscriptions[1].subscription.source.platform == SubscriptionSourcePlatform.github

    async def test_subscribe_skip_subscription(self) -> None:
        self.skipTest("I'm not sure this test is asserting the right thing, please check")
        # when links don't point to actual files in repo,
        # subscription parsing fails, causing subscription to exit early
        input_links = [
            ("https://github.com/eave-fyi/", LinkType.github),
            ("http://github.enterprise.com/the-org/repo-name/", LinkType.github),
        ]
        subscriptions = await link_handler.subscribe_to_file_changes(
            eave_team_id=self.anyuuid(),
            urls=input_links,
        )
        assert len(subscriptions) == 2
