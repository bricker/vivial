from typing import TypedDict
from .ev_connector_type import EVConnectorType

class ConnectorAggregation(TypedDict, total=False):
    type: EVConnectorType
    maxChargeRateKw: float
    count: int
    availabilityLastUpdateTime: str
    availableCount: int
    outOfServiceCount: int
