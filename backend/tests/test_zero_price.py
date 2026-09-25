"""Unit tests for Zero Price bug prevention and validation rules.

Tests Bug 1 fix:
- Existing products (Passo 4): New price <= 0 must not overwrite existing catalog price.
  Must be blocked with BLOCKED_ZERO_PRICE blocker issue.
- New products (Passo 5): Items with price <= 0 must be ignored with IGNORED_ZERO_PRICE.
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


@pytest.fixture
def standard_profile() -> CommercialProfile:
    return CommercialProfile(
        code="MANO",
        name="ManoMano Catalog",
        price_rule=PriceRule(
            max_variation_threshold=0.30,
            allow_zero_price=False,
            reject_negative=True,
        ),
        stock_rule=StockRule(min_stock_activation=3),
    )


class TestZeroPriceExistingProducts:
    """Passo 4 legacy bug: existing catalog item receives zero or negative price."""

    def test_existing_product_with_zero_price_is_blocked(self, standard_profile):
        target_catalog = [
            {
                "internal_identifier": "PROD-001",
                "original_price": 100.0,
                "quantity": 10,
                "is_active": True,
                "sold_out": False,
            }
        ]
        source_records = [
            {
                "REFERENCIA": "PROD-001",
                "PRECO": 0.0,
                "STOCK": 15,
            }
        ]

        result = process_price_table(source_records, target_catalog, standard_profile)

        # Must report blocker issue
        assert result.has_blockers is True
        zero_issues = [
            i for i in result.issues
            if i.code in ("BLOCKED_ZERO_PRICE", "ZERO_PRICE_REJECTED")
        ]
        assert len(zero_issues) == 1
        assert zero_issues[0].severity == IssueSeverity.BLOCKER
        assert "PROD-001" in zero_issues[0].message or zero_issues[0].details.get("reference") == "PROD-001"

        # Item result check
        item = result.items[0]
        assert item.decision_code in (DecisionCode.BLOCKED_ZERO_PRICE, DecisionCode.ZERO_PRICE_REJECTED)
        assert item.old_price == 100.0
        assert item.new_price == 0.0

        # Summary check
        assert result.summary.blocked_zero_price == 1
        assert result.summary.updated == 0

        # Target catalog price MUST NOT be overwritten to 0.0
        output_prod = next(
            p for p in result.output_records
            if p["internal_identifier"] == "PROD-001"
        )
        assert output_prod["original_price"] == 100.0

    def test_existing_product_with_negative_price_is_blocked(self, standard_profile):
        target_catalog = [
            {
                "internal_identifier": "PROD-002",
                "original_price": 50.0,
                "quantity": 5,
                "is_active": True,
                "sold_out": False,
            }
        ]
        source_records = [
            {
                "REFERENCIA": "PROD-002",
                "PRECO": -10.0,
                "STOCK": 5,
            }
        ]

        result = process_price_table(source_records, target_catalog, standard_profile)
        assert result.has_blockers is True
        assert result.summary.updated == 0

        output_prod = result.output_records[0]
        assert output_prod["original_price"] == 50.0

    def test_existing_product_zero_price_allowed_if_configured(self):
        profile = CommercialProfile(
            code="MANO_PERMISSIVE",
            name="Permissive Profile",
            price_rule=PriceRule(allow_zero_price=True, max_variation_threshold=1.0),
            stock_rule=StockRule(min_stock_activation=1),
        )
        target_catalog = [
            {
                "internal_identifier": "PROD-003",
                "original_price": 100.0,
                "quantity": 5,
                "is_active": True,
                "sold_out": False,
            }
        ]
        source_records = [
            {
                "REFERENCIA": "PROD-003",
                "PRECO": 0.0,
                "STOCK": 5,
            }
        ]

        result = process_price_table(source_records, target_catalog, profile)
        assert result.has_blockers is False
        assert result.summary.blocked_zero_price == 0
        assert result.summary.updated == 1
        assert result.output_records[0]["original_price"] == 0.0


class TestZeroPriceNewProducts:
    """Passo 5 legacy behavior: new product in source has price zero."""

    def test_new_product_with_zero_price_is_ignored(self, standard_profile):
        target_catalog = []  # Empty target, all source items are new candidate products
        source_records = [
            {
                "REFERENCIA": "NEW-PROD-001",
                "PRECO": 0.0,
                "STOCK": 20,
                "DESIGNACAO": "New Product Zero Price",
            }
        ]

        result = process_price_table(source_records, target_catalog, standard_profile)

        # Must not add the product to target catalog
        assert len(result.output_records) == 0
        assert result.summary.new_added == 0
        assert result.summary.ignored_zero_price == 1

        # Item decision must indicate IGNORED_ZERO_PRICE
        item = result.items[0]
        assert item.decision_code == DecisionCode.IGNORED_ZERO_PRICE

        # Issue should be recorded (severity INFO/WARNING)
        zero_issues = [i for i in result.issues if i.code == "IGNORED_ZERO_PRICE"]
        assert len(zero_issues) == 1
        assert zero_issues[0].severity in (IssueSeverity.INFO, IssueSeverity.WARNING)
