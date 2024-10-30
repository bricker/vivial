from typing import TypedDict

from .ev_connector_type import EVConnectorType


class ConnectorAggregation(TypedDict, total=False):
    """https://developers.google.com/maps/documentation/places/web-service/reference/rest/v1/places#ConnectorAggregation"""

    type: EVConnectorType
    maxChargeRateKw: float
    count: int
    availabilityLastUpdateTime: str
    availableCount: int
    outOfServiceCount: int
