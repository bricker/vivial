from typing import TypeVar

import eave.stdlib.core_api.client as eave_core
import eave.stdlib.link_handler as link_handler
import mockito
import pytest
from eave.stdlib.core_api.models import SupportedLink
from eave.stdlib.third_party_api_clients.github import GitHubClient, GithubRepository
from pydantic import UUID4

T = TypeVar("T")
pytest_plugins = ("pytest_asyncio",)


async def mock_coroutine(value: T) -> T:
    return value


@pytest.mark.parametrize(
    "input_link, expected_result",
    [
        ("https://github.com", [SupportedLink.github]),
        ("https://github.enterprise.com", [SupportedLink.github]),
        ("https://github.com/eave-fyi/eave-monorepo/blob/main/.gitignore", [SupportedLink.github]),
        ("http://github.enterprise.com/the-org/repo-name/path/to/file.txt", [SupportedLink.github]),
        ("https://api.github.com", []),
        ("https://githubby.com", []),
        ("https://google.com", []),
    ],
)
def test_filter_supported_links(input_link: str, expected_result: list[SupportedLink]) -> None:
    result = link_handler.filter_supported_links([input_link])
    assert result == [(input_link, supported) for supported in expected_result]


@pytest.mark.asyncio
async def test_map_link_content() -> None:
    # TODO uncomment when code is complete in link_handler
    # mockito.when2(core_api.get_installations, **mockito.KWARGS).thenReturn(fixtures.core_api.installations)
    mockito.when2(GitHubClient.get_file_content, *mockito.args).thenReturn(
        mock_coroutine("dummy gh content")
    ).thenReturn(mock_coroutine("dummy gh content"))

    dummy_id = UUID4("7b1b3e6a-5a28-4e14-9cad-4a3cbebeee2c")
    input_links = [
        ("https://github.com/eave-fyi/eave-monorepo/blob/main/.gitignore", SupportedLink.github),
        ("http://github.enterprise.com/the-org/repo-name/path/to/file.txt", SupportedLink.github),
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
    mockito.unstub()


@pytest.mark.asyncio
async def test_subscribe_successful_subscription() -> None:
    mockito.when2(GitHubClient.get_repo, *mockito.args).thenReturn(
        mock_coroutine(GithubRepository(node_id="1", full_name="eave-fyi/eave-monorepo"))
    )  # .thenReturn(GithubRepository(node_id="1", full_name="the-org/repo-name"))
    mockito.when2(eave_core.create_subscription, **mockito.kwargs).thenReturn(mock_coroutine(None))

    dummy_id = UUID4("7b1b3e6a-5a28-4e14-9cad-4a3cbebeee2c")
    input_links = [
        ("https://github.com/eave-fyi/eave-monorepo/blob/main/.gitignore", SupportedLink.github),
        ("http://github.enterprise.com/the-org/repo-name/path/to/file.txt", SupportedLink.github),
    ]
    await link_handler.subscribe(
        eave_team_id=dummy_id,
        urls=input_links,
    )

    mockito.verifyStubbedInvocationsAreUsed()
    mockito.unstub()


@pytest.mark.asyncio
async def test_subscribe_skip_subscription() -> None:
    mockito.when2(GitHubClient.get_repo, *mockito.args).thenReturn(
        mock_coroutine(GithubRepository(node_id="1", full_name="the-org/repo-name"))
    )

    dummy_id = UUID4("7b1b3e6a-5a28-4e14-9cad-4a3cbebeee2c")
    # links don't point to actual files in repo; point to org or repo
    input_links = [
        ("https://github.com/eave-fyi/", SupportedLink.github),
        ("http://github.enterprise.com/the-org/repo-name/", SupportedLink.github),
    ]
    await link_handler.subscribe(
        eave_team_id=dummy_id,
        urls=input_links,
    )

    mockito.verifyStubbedInvocationsAreUsed()
    mockito.unstub()
