from pydantic import UUID4
from eave.stdlib.third_party_api_clients.github import GitHubClient
import pytest
import mockito

import eave.stdlib.link_handler as link_handler
from eave.stdlib.core_api.models import SupportedLink


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


async def test_map_link_content() -> None:
    # mockito.when2(core_api.get_installations, **mockito.KWARGS).thenReturn(fixtures.core_api.installations)
    mockito.when2(GitHubClient.get_file_content, **mockito.kwargs).thenReturn("dummy gh content")

    dummy_id = UUID4("7b1b3e6a-5a28-4e14-9cad-4a3cbebeee2c")
    input_links = [
        ("https://github.com/eave-fyi/eave-monorepo/blob/main/.gitignore", SupportedLink.github),
        ("http://github.enterprise.com/the-org/repo-name/path/to/file.txt", SupportedLink.github),
    ]
    actual_result = await link_handler.map_link_content(
        eave_team_id=dummy_id,
        links=input_links,
    )

    expected_result = [
        "dummy gh content",
        "dummy gh content",
    ]
    assert actual_result == expected_result


async def test_subscribe() -> None:
    pytest.skip()
