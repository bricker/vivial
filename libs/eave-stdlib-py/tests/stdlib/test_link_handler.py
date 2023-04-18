from typing import Optional
import pytest
import eave.stdlib.link_handler as link_handler

@pytest.mark.parametrize("input_link, expected_match, expected_type", [
    ("https://github.com", True, link_handler.SupportedLink.github),
    ("https://github.enterprise.com", True, link_handler.SupportedLink.github),
    ("https://www.github.com", True, link_handler.SupportedLink.github),
    ("https://github.com/eave-fyi/eave-monorepo/blob/main/.gitignore", True, link_handler.SupportedLink.github),
    ("http://github.enterprise.com/the-org/repo-name/path/to/file.txt", True, link_handler.SupportedLink.github),
    ("https://example.github.com", False, None),
    ("https://notgithub.com", False, None),
    ("https://google.com", False, None),
])
def test_github_regex(input_link: str, expected_match: bool, expected_type: Optional[link_handler.SupportedLink]) -> None:
    match, link_type = link_handler.is_supported_link(input_link)
    assert match == expected_match
    assert link_type == expected_type