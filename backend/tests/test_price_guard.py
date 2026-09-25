"""Unit tests for configurable price guard protection and variation limits.

Tests Bug 3 fix:
- Legacy bug: Hardcoded 30% variation limit in main.py.
- New engine: Dynamically reads max_variation_threshold from CommercialProfile.price_rule
  (e.g. 0.10, 0.15, 0.30, 0.50).
- Variations within threshold are approved.
- Variations exceeding threshold are blocked with BLOCKED_PRICE_VARIATION and BLOCKER severity.
- Target price is NOT modified when blocked.
- Safe calculation preventing ZeroDivisionError.
"""

import pytest

from backend.app.domain.engine import process_price_table
from backend.app.domain.models import (
    CommercialProfile,
    DecisionCode,
    IssueSeverity,
    PriceRule,
    StockRule,
)


def create_profile(threshold: float) -> CommercialProfile:
    return CommercialProfile(
        code="TEST_PROFILE",
        name="Test Profile",
        price_rule=PriceRule(
            max_variation_threshold=threshold,
            allow_zero_price=False,
            reject_negative=True,
        ),
        stock_rule=StockRule(min_stock_activation=3),
    )


class TestConfigurablePriceGuard:
    """Verifies that the price variation threshold is dynamically evaluated from profile."""

    def test_threshold_15_percent_accepts_10_percent_rejects_20_percent(self):
        profile = create_profile(threshold=0.15)
        target_catalog = [
            {
                "internal_identifier": "PROD-ACCEPT",
                "original_price": 100.0,
                "quantity": 10,
                "is_active": True,
                "sold_out": False,
            },
            {
                "internal_identifier": "PROD-REJECT",
                "original_price": 100.0,
                "quantity": 10,
                "is_active": True,
                "sold_out": False,
            },
        ]
        source_records = [
            {"REFERENCIA": "PROD-ACCEPT", "PRECO": 110.0, "STOCK": 10},  # +10% -> OK
            {"REFERENCIA": "PROD-REJECT", "PRECO": 120.0, "STOCK": 10},  # +20% -> Blocked
        ]

        result = process_price_table(source_records, target_catalog, profile)

        # Check issues
        guard_issues = [
            i for i in result.issues
            if i.code in ("BLOCKED_PRICE_VARIATION", "BLOQUEADO_VARIACAO_EXCESSIVA")
        ]
        assert len(guard_issues) == 1
        assert guard_issues[0].severity == IssueSeverity.BLOCKER
        assert "PROD-REJECT" in guard_issues[0].message or guard_issues[0].details.get("reference") == "PROD-REJECT"

        # Summary counts
        assert result.summary.updated == 1
        assert result.summary.blocked_price_variation == 1

        # Check output records
        prod_accept = next(p for p in result.output_records if p["internal_identifier"] == "PROD-ACCEPT")
        prod_reject = next(p for p in result.output_records if p["internal_identifier"] == "PROD-REJECT")

        assert prod_accept["original_price"] == 110.0
        assert prod_reject["original_price"] == 100.0  # NOT updated!

    def test_threshold_30_percent_boundaries(self):
        profile = create_profile(threshold=0.30)
        target_catalog = [
            {"internal_identifier": "PROD-5PCT", "original_price": 100.0, "quantity": 5},
            {"internal_identifier": "PROD-29PCT", "original_price": 100.0, "quantity": 5},
            {"internal_identifier": "PROD-31PCT", "original_price": 100.0, "quantity": 5},
            {"internal_identifier": "PROD-150PCT", "original_price": 100.0, "quantity": 5},
        ]
        source_records = [
            {"REFERENCIA": "PROD-5PCT", "PRECO": 105.0, "STOCK": 5},    # +5% -> OK
            {"REFERENCIA": "PROD-29PCT", "PRECO": 129.9, "STOCK": 5},   # +29.9% -> OK
            {"REFERENCIA": "PROD-31PCT", "PRECO": 130.1, "STOCK": 5},   # +30.1% -> Blocked
            {"REFERENCIA": "PROD-150PCT", "PRECO": 250.0, "STOCK": 5},  # +150% -> Blocked
        ]

        result = process_price_table(source_records, target_catalog, profile)

        assert result.summary.updated == 2
        assert result.summary.blocked_price_variation == 2

        out_5 = next(p for p in result.output_records if p["internal_identifier"] == "PROD-5PCT")
        out_29 = next(p for p in result.output_records if p["internal_identifier"] == "PROD-29PCT")
        out_31 = next(p for p in result.output_records if p["internal_identifier"] == "PROD-31PCT")
        out_150 = next(p for p in result.output_records if p["internal_identifier"] == "PROD-150PCT")

        assert out_5["original_price"] == 105.0
        assert out_29["original_price"] == 129.9
        assert out_31["original_price"] == 100.0
        assert out_150["original_price"] == 100.0

    def test_negative_variation_exceeding_threshold_is_blocked(self):
        profile = create_profile(threshold=0.30)
        target_catalog = [
            {"internal_identifier": "PROD-DROP", "original_price": 100.0, "quantity": 10}
        ]
        source_records = [
            {"REFERENCIA": "PROD-DROP", "PRECO": 60.0, "STOCK": 10}  # -40% drop -> Blocked
        ]

        result = process_price_table(source_records, target_catalog, profile)

        assert result.summary.blocked_price_variation == 1
        assert result.summary.updated == 0
        out_prod = result.output_records[0]
        assert out_prod["original_price"] == 100.0

    def test_threshold_10_percent_and_50_percent(self):
        profile_10 = create_profile(threshold=0.10)
        profile_50 = create_profile(threshold=0.50)
        target = [{"internal_identifier": "PROD-GUARD", "original_price": 100.0, "quantity": 5}]

        # +12% variation: blocked under 10% threshold
        res_10 = process_price_table([{"REFERENCIA": "PROD-GUARD", "PRECO": 112.0, "STOCK": 5}], target, profile_10)
        assert res_10.summary.blocked_price_variation == 1
        assert res_10.summary.updated == 0

        # +40% variation: approved under 50% threshold
        res_50_ok = process_price_table([{"REFERENCIA": "PROD-GUARD", "PRECO": 140.0, "STOCK": 5}], target, profile_50)
        assert res_50_ok.summary.updated == 1
        assert res_50_ok.output_records[0]["original_price"] == 140.0

        # +60% variation: blocked under 50% threshold
        res_50_block = process_price_table([{"REFERENCIA": "PROD-GUARD", "PRECO": 160.0, "STOCK": 5}], target, profile_50)
        assert res_50_block.summary.blocked_price_variation == 1
        assert res_50_block.summary.updated == 0

    def test_zero_or_null_old_price_does_not_raise_zero_division(self):
        profile = create_profile(threshold=0.30)
        target_catalog = [
            {"internal_identifier": "PROD-NULL", "original_price": None, "quantity": 10},
            {"internal_identifier": "PROD-ZERO", "original_price": 0.0, "quantity": 10},
        ]
        source_records = [
            {"REFERENCIA": "PROD-NULL", "PRECO": 50.0, "STOCK": 10},
            {"REFERENCIA": "PROD-ZERO", "PRECO": 50.0, "STOCK": 10},
        ]

        # Must execute cleanly without ZeroDivisionError
        result = process_price_table(source_records, target_catalog, profile)
        assert result is not None
        assert len(result.output_records) == 2
