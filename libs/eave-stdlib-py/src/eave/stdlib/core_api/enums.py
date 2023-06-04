import enum


class LinkType(enum.StrEnum):
    """
    Link types that we support fetching content from for integration into AI documentation creation.
    """

    github = "github"
