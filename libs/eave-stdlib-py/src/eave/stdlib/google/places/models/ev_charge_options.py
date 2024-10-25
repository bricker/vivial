from dataclasses import dataclass
from .connector_aggregation import ConnectorAggregation

@dataclass
class EVChargeOptions:
    connectorCount: int
    connectorAggregation: list[ConnectorAggregation]
