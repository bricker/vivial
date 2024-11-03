from typing import Required, TypedDict

from eave.stdlib.eventbrite.models.shared import CartesianCoordinates, Image


class CropMask(TypedDict, total=False):
    """The crop mask applied to the original image"""

    top_left: CartesianCoordinates
    """Coordinate for top-left corner of crop mask"""

    width: int
    """Crop mask width"""

    height: int
    """Crop mask height"""


class OriginalImage(TypedDict, total=False):
    """The original image (for a Logo object)"""

    url: str
    """The URL of the image"""

    width: int
    """The width of the image in pixels"""

    height: int
    """The height of the image in pixels"""

class Logo(Image, total=False):
    crop_mask: CropMask | None
    """The crop mask applied to the original image"""

    original: OriginalImage
    """The original image"""

    aspect_ratio: str
    """The aspect ratio of the cropped image"""

    edge_color: str
    """The edge color of the image in hexadecimal representation"""

    edge_color_set: bool
    """True if the edge color has been set"""
