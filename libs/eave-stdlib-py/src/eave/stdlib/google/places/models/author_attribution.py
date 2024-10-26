from typing import TypedDict

class AuthorAttribution(TypedDict, total=False):
    displayName: str
    uri: str
    photoUri: str
