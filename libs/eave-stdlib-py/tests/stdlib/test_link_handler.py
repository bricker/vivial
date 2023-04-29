from typing import Optional

import eave.stdlib.link_handler as link_handler
import pytest
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
def test_supported_links(input_link: str, expected_result: list[SupportedLink]) -> None:
    result = link_handler.filter_supported_links([input_link])
    assert result == [(input_link, supported) for supported in expected_result]
