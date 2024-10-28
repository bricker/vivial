from typing import TypedDict

from .connector_aggregation import ConnectorAggregation


class EVChargeOptions(TypedDict, total=False):
    connectorCount: int
    connectorAggregation: list[ConnectorAggregation]
