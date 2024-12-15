
from eave.core.graphql.types.pricing import CostBreakdown

from ..base import BaseTestCase


class TestCostBreakdown(BaseTestCase):
    async def test_cost_breakdown_multiplication(self) -> None:
        cost_breakdown = CostBreakdown(base_cost_cents=100, fee_cents=10, tax_cents=5)

        assert cost_breakdown.total_cost_cents_internal == 115

        doubled_breakdown = cost_breakdown * 2
        assert doubled_breakdown.base_cost_cents == 200
        assert doubled_breakdown.fee_cents == 20
        assert doubled_breakdown.tax_cents == 10
        assert doubled_breakdown.total_cost_cents_internal == 230
