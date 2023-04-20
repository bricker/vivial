from typing import Optional
import pytest
import eave.stdlib.link_handler as link_handler
from eave.stdlib.core_api.models import SupportedLink


@pytest.mark.parametrize(
    "input_link, expected_match, expected_type",
    [
        ("https://github.com", True, SupportedLink.github),
        ("https://github.enterprise.com", True, SupportedLink.github),
        ("https://github.com/eave-fyi/eave-monorepo/blob/main/.gitignore", True, SupportedLink.github),
        ("http://github.enterprise.com/the-org/repo-name/path/to/file.txt", True, SupportedLink.github),
        ("https://api.github.com", False, None),
        ("https://githubby.com", False, None),
        ("https://google.com", False, None),
    ],
)
def test_github_regex(input_link: str, expected_match: bool, expected_type: Optional[SupportedLink]) -> None:
    match, link_type = link_handler.is_supported_link(input_link)
    assert match == expected_match
    assert link_type == expected_type
