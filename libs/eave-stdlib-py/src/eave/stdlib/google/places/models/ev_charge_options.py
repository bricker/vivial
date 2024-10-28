from typing import TypedDict

from .connector_aggregation import ConnectorAggregation


class EVChargeOptions(TypedDict, total=False):
    """https://developers.google.com/maps/documentation/places/web-service/reference/rest/v1/places#EVChargeOptions"""

    connectorCount: int
    connectorAggregation: list[ConnectorAggregation]
