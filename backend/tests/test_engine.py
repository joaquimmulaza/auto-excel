"""Unit tests for the core domain engine: TableProcessor / process_price_table.

Verifies:
- Fully deterministic pure in-memory execution.
- No CLI dependencies (no argparse, sys.exit, print).
- Existing product updates (price, stock, activation status).
- Stock activation rules (stock >= min_stock_activation -> active, else sold_out).
- New product addition (only if eligible and stock >= min_stock_activation).
- Complete ProcessResult structure (items, issues, summary, output_records).
"""

import copy
import pytest

from backend.app.domain.engine import TableProcessor, process_price_table
from backend.app.domain.models import (
    CommercialProfile,
    DecisionCode,
    IssueSeverity,
    PriceRule,
    ProcessResult,
    StockRule,
)


@pytest.fixture
def profile() -> CommercialProfile:
    return CommercialProfile(
        code="MANO",
        name="ManoMano Default",
        price_rule=PriceRule(
            max_variation_threshold=0.30,
            allow_zero_price=False,
            reject_negative=True,
        ),
        stock_rule=StockRule(min_stock_activation=3),
    )


class TestDomainEngine:
    """Core domain processor test suite."""

    def test_pure_in_memory_execution_returns_structured_result(self, profile):
        source_records = [
            {"REFERENCIA": "REF-001", "PRECO": 105.0, "STOCK": 10, "DESIGNACAO": "Item 1"}
        ]
        target_catalog = [
            {
                "internal_identifier": "REF-001",
                "original_price": 100.0,
                "quantity": 2,
                "is_active": False,
                "sold_out": True,
            }
        ]

        result = process_price_table(source_records, target_catalog, profile)

        assert isinstance(result, ProcessResult)
        assert len(result.items) == 1
        assert len(result.output_records) == 1
        assert result.summary.total_source_rows == 1
        assert result.summary.total_target_rows == 1
        assert result.summary.updated == 1
        assert result.has_blockers is False

    def test_updates_existing_product_and_activates_stock(self, profile):
        # Product had stock 1 (< 3) and was inactive; now gets stock 5 (>= 3) -> should activate
        source_records = [
            {"REFERENCIA": "REF-ACTIVATE", "PRECO": 110.0, "STOCK": 5}
        ]
        target_catalog = [
            {
                "internal_identifier": "REF-ACTIVATE",
                "original_price": 100.0,
                "quantity": 1,
                "is_active": False,
                "sold_out": True,
            }
        ]

        result = process_price_table(source_records, target_catalog, profile)

        out_item = result.output_records[0]
        assert out_item["original_price"] == 110.0
        assert out_item["quantity"] == 5
        assert out_item["is_active"] is True
        assert out_item["sold_out"] is False

        # Job item result details
        item_res = result.items[0]
        assert item_res.decision_code == DecisionCode.UPDATE
        assert item_res.old_price == 100.0
        assert item_res.new_price == 110.0
        assert item_res.old_stock == 1
        assert item_res.new_stock == 5

    def test_existing_product_deactivates_when_stock_below_threshold(self, profile):
        # Product had stock 10; now gets stock 2 (< min_stock_activation 3) -> should deactivate
        source_records = [
            {"REFERENCIA": "REF-DEACTIVATE", "PRECO": 50.0, "STOCK": 2}
        ]
        target_catalog = [
            {
                "internal_identifier": "REF-DEACTIVATE",
                "original_price": 50.0,
                "quantity": 10,
                "is_active": True,
                "sold_out": False,
            }
        ]

        result = process_price_table(source_records, target_catalog, profile)

        out_item = result.output_records[0]
        assert out_item["quantity"] == 2
        assert out_item["is_active"] is False
        assert out_item["sold_out"] is True

    def test_adds_eligible_new_product(self, profile):
        source_records = [
            {
                "REFERENCIA": "NEW-REF-999",
                "PRECO": 85.50,
                "STOCK": 10,
                "DESIGNACAO": "New Product Test",
            }
        ]
        target_catalog = []

        result = process_price_table(source_records, target_catalog, profile)

        assert result.summary.new_added == 1
        assert len(result.output_records) == 1

        new_prod = result.output_records[0]
        assert new_prod["internal_identifier"] == "NEW-REF-999"
        assert new_prod["original_price"] == 85.50
        assert new_prod["quantity"] == 10
        assert new_prod["is_active"] is True
        assert new_prod["sold_out"] is False

        item_res = result.items[0]
        assert item_res.decision_code == DecisionCode.NEW_PRODUCT

    def test_ignores_new_product_with_insufficient_stock(self, profile):
        source_records = [
            {
                "REFERENCIA": "LOW-STOCK-NEW",
                "PRECO": 90.0,
                "STOCK": 2,  # < 3
                "DESIGNACAO": "Low Stock New",
            }
        ]
        target_catalog = []

        result = process_price_table(source_records, target_catalog, profile)

        assert result.summary.new_added == 0
        assert result.summary.ignored_stock == 1
        assert len(result.output_records) == 0

        item_res = result.items[0]
        assert item_res.decision_code == DecisionCode.IGNORED_STOCK

    def test_input_immutability(self, profile):
        """Engine should not mutate the caller's input lists directly."""
        source_records = [
            {"REFERENCIA": "REF-IMMUTABLE", "PRECO": 110.0, "STOCK": 5}
        ]
        target_catalog = [
            {
                "internal_identifier": "REF-IMMUTABLE",
                "original_price": 100.0,
                "quantity": 1,
            }
        ]
        source_copy = copy.deepcopy(source_records)
        target_copy = copy.deepcopy(target_catalog)

        process_price_table(source_records, target_catalog, profile)

        assert source_records == source_copy
        assert target_catalog == target_copy

    def test_table_processor_class_interface(self, profile):
        """TableProcessor class can be instantiated and executed cleanly."""
        processor = TableProcessor(profile=profile)
        source_records = [{"REFERENCIA": "REF-01", "PRECO": 50.0, "STOCK": 5}]
        target_catalog = [{"internal_identifier": "REF-01", "original_price": 50.0, "quantity": 1}]

        result = processor.process(source_records, target_catalog)
        assert isinstance(result, ProcessResult)
        assert result.summary.updated == 1
