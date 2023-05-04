from typing import Generator, TypeVar

import eave.stdlib.core_api.client as eave_core
import eave.stdlib.core_api.operations as operations
import eave.stdlib.core_api.models as models
import eave.stdlib.link_handler as link_handler
import eave.stdlib.eave_origins as eave_origins
import mockito
import pytest
from eave.stdlib.core_api.models import LinkType
from eave.stdlib.third_party_api_clients.github import GitHubClient, GithubRepository
from pydantic import UUID4


# apply plugin allowing async funcational tests
pytest_plugins = ("pytest_asyncio",)
# set a core_api client origin to make tests not crash from it being unset
eave_core.set_origin(eave_origins.EaveOrigin.eave_slack_app)

T = TypeVar("T")


async def mock_coroutine(value: T) -> T:
    return value

@pytest.fixture
def setup_teardown() -> Generator[None, None, None]:
    # setup
    yield
    # teardown
    mockito.unstub()


@pytest.mark.parametrize(
    "input_link, expected_result",
    [
        ("https://github.com", [LinkType.github]),
        ("https://github.enterprise.com", [LinkType.github]),
        ("https://github.com/eave-fyi/eave-monorepo/blob/main/.gitignore", [LinkType.github]),
        ("http://github.enterprise.com/the-org/repo-name/path/to/file.txt", [LinkType.github]),
        ("https://api.github.com", []),
        ("https://githubby.com", []),
        ("https://google.com", []),
    ],
)
def test_filter_supported_links(input_link: str, expected_result: list[LinkType]) -> None:
    result = link_handler.filter_supported_links([input_link])
    assert result == [(input_link, supported) for supported in expected_result]


@pytest.mark.asyncio
async def test_map_link_content(setup_teardown) -> None:
    setup_shared_mocks()
    mockito.when2(GitHubClient.get_file_content, *mockito.args).thenReturn(
        mock_coroutine("dummy gh content")
    ).thenReturn(mock_coroutine("dummy gh content"))

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
    # mockito.unstub()


@pytest.mark.asyncio
async def test_subscribe_successful_subscription(setup_teardown) -> None:
    setup_shared_mocks()
    mockito.when2(GitHubClient.get_repo, *mockito.args).thenReturn(
        mock_coroutine(GithubRepository(node_id="1", full_name="eave-fyi/eave-monorepo"))
    ).thenReturn(
        mock_coroutine(GithubRepository(node_id="1", full_name="eave-fyi/eave-monorepo"))
    )
    mockito.when2(eave_core.create_subscription, **mockito.kwargs).thenReturn(mock_coroutine(None))
    mockito.when2(GitHubClient._create_jwt, *mockito.args).thenReturn("dummy jwt")


    dummy_id = UUID4("7b1b3e6a-5a28-4e14-9cad-4a3cbebeee2c")
    input_links = [
        ("https://github.com/eave-fyi/eave-monorepo/blob/main/.gitignore", LinkType.github),
        ("http://github.enterprise.com/the-org/repo-name/path/to/file.txt", LinkType.github),
    ]
    await link_handler.subscribe(
        eave_team_id=dummy_id,
        urls=input_links,
    )

    mockito.verifyStubbedInvocationsAreUsed()
    # mockito.unstub()


@pytest.mark.asyncio
async def test_subscribe_skip_subscription(setup_teardown) -> None:
    setup_shared_mocks()
    mockito.when2(GitHubClient.get_repo, *mockito.args).thenReturn(
        mock_coroutine(GithubRepository(node_id="1", full_name="the-org/repo-name"))
    ).thenReturn(
        mock_coroutine(GithubRepository(node_id="1", full_name="the-org/repo-name"))
    )

    dummy_id = UUID4("7b1b3e6a-5a28-4e14-9cad-4a3cbebeee2c")
    # when links don't point to actual files in repo,
    # subscription parsing fails, causing subscription to exit early
    input_links = [
        ("https://github.com/eave-fyi/", LinkType.github),
        ("http://github.enterprise.com/the-org/repo-name/", LinkType.github),
    ]
    await link_handler.subscribe(
        eave_team_id=dummy_id,
        urls=input_links,
    )

    mockito.verifyStubbedInvocationsAreUsed()
    # mockito.unstub()


def setup_shared_mocks() -> None:
    dummy_id = UUID4("7b1b3e6a-5a28-4e14-9cad-4a3cbebeee2c")
    mockito.when2(eave_core.get_team, **mockito.KWARGS).thenReturn(
        mock_coroutine(
            operations.GetAuthenticatedAccountTeamIntegrations.ResponseBody(
                account=models.AuthenticatedAccount(
                    id=dummy_id,
                    auth_provider=models.AuthProvider.google,
                    access_token="dummy token",
                ),
                team=models.Team(
                    id=dummy_id,
                    name="Team name",
                    document_platform=models.DocumentPlatform.confluence,
                ),
                integrations=models.Integrations(
                    github=models.GithubInstallation(
                        id=dummy_id,
                        team_id=dummy_id,
                        github_install_id="install id",
                    ),
                    slack=None,
                    atlassian=None,
                ),
            )
        )
    )