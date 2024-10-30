from typing import TypedDict


class PlusCode(TypedDict, total=False):
    """https://developers.google.com/maps/documentation/places/web-service/reference/rest/v1/places#PlusCode"""

    globalCode: str
    compoundCode: str
