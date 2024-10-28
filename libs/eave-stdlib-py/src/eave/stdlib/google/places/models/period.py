from typing import TypedDict

from .point import Point


class Period(TypedDict, total=False):
    open: Point
    close: Point
