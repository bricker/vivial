from typing import TypedDict


class ParkingOptions(TypedDict, total=False):
    freeParkingLot: bool
    paidParkingLot: bool
    freeStreetParking: bool
    paidStreetParking: bool
    valetParking: bool
    freeGarageParking: bool
    paidGarageParking: bool
