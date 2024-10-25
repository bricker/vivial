from dataclasses import dataclass

@dataclass
class ParkingOptions:
    freeParkingLot: bool
    paidParkingLot: bool
    freeStreetParking: bool
    paidStreetParking: bool
    valetParking: bool
    freeGarageParking: bool
    paidGarageParking: bool
