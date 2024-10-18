from typing import TypedDict

from eave.stdlib.eventbrite.models.shared import CartesianCoordinates


class CropMask(TypedDict, total=False):
    """The crop mask applied to the original image"""

    top_left: CartesianCoordinates | None
    """Coordinate for top-left corner of crop mask"""

    width: int | None
    """Crop mask width"""

    height: int | None
    """Crop mask height"""


class OriginalImage(TypedDict, total=False):
    """The original image (for a Logo object)"""

    url: str | None
    """The URL of the image"""

    width: int | None
    """The width of the image in pixels"""

    height: int | None
    """The height of the image in pixels"""


class Logo(TypedDict, total=False):
    id: str | None
    """The image's ID"""

    url: str | None
    """The URL of the image"""

    crop_mask: CropMask | None
    """The crop mask applied to the original image"""

    original: OriginalImage | None
    """The original image"""

    aspect_ratio: str | None
    """The aspect ratio of the cropped image"""

    edge_color: str | None
    """The edge color of the image in hexadecimal representation"""

    edge_color_set: bool | None
    """True if the edge color has been set"""
