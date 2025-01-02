from eave.core.graphql.types.cost_breakdown import CostBreakdown

from ..base import BaseTestCase


class TestCostBreakdown(BaseTestCase):
    async def test_cost_breakdown_multiplication(self) -> None:
        cost_breakdown = CostBreakdown(base_cost_cents=100, fee_cents=10, tax_cents=5)

        assert cost_breakdown.calculate_total_cost_cents() == 115

        doubled_breakdown = cost_breakdown * 2
        assert doubled_breakdown.base_cost_cents == 200
        assert doubled_breakdown.fee_cents == 20
        assert doubled_breakdown.tax_cents == 10
        assert doubled_breakdown.calculate_total_cost_cents() == 230

    async def test_cost_breakdown_addition(self) -> None:
        cost_breakdown1 = CostBreakdown(base_cost_cents=100, fee_cents=10, tax_cents=5)
        cost_breakdown2 = CostBreakdown(base_cost_cents=200, fee_cents=20, tax_cents=10)

        added_breakdown = cost_breakdown1 + cost_breakdown2
        assert added_breakdown.base_cost_cents == 300
        assert added_breakdown.fee_cents == 30
        assert added_breakdown.tax_cents == 15
        assert added_breakdown.calculate_total_cost_cents() == 345

    async def test_cost_breakdown_add_equals(self) -> None:
        cost_breakdown1 = CostBreakdown(base_cost_cents=100, fee_cents=10, tax_cents=5)
        cost_breakdown2 = CostBreakdown(base_cost_cents=200, fee_cents=20, tax_cents=10)

        cost_breakdown1 += cost_breakdown2
        assert cost_breakdown1.base_cost_cents == 300
        assert cost_breakdown1.fee_cents == 30
        assert cost_breakdown1.tax_cents == 15
        assert cost_breakdown1.calculate_total_cost_cents() == 345
