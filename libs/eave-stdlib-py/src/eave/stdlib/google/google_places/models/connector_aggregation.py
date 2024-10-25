from dataclasses import dataclass
from .ev_connector_type import EVConnectorType

@dataclass
class ConnectorAggregation:
    type: EVConnectorType
    maxChargeRateKw: float
    count: int
    availabilityLastUpdateTime: str
    availableCount: int
    outOfServiceCount: int
