from typing import TypedDict


class LocalizedText(TypedDict, total=False):
    text: str
    languageCode: str
