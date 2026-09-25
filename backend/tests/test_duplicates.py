"""Unit tests for duplicate reference detection in source dataset.

Tests Bug 2 fix:
- Legacy bug: dict(zip(...)) silently overwrote repeated items in source tables.
- New engine: Detects duplicate normalized references proactively, emits BLOCKER
  issues detailing duplicate references and affected row numbers, and prevents
  silent data corruption.
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
def profile() -> CommercialProfile:
    return CommercialProfile(
        code="MANO",
        name="ManoMano",
        price_rule=PriceRule(max_variation_threshold=0.30),
        stock_rule=StockRule(min_stock_activation=3),
    )


class TestDuplicateReferences:
    """Verifies that duplicate references in source records are caught and blocked."""

    def test_duplicate_references_trigger_blocker_issue(self, profile):
        # Two rows with identical reference in source
        source_records = [
            {"REFERENCIA": "REF-DUP-001", "PRECO": 50.0, "STOCK": 10},
            {"REFERENCIA": "REF-DUP-001", "PRECO": 55.0, "STOCK": 12},
        ]
        target_catalog = [
            {
                "internal_identifier": "REF-DUP-001",
                "original_price": 50.0,
                "quantity": 5,
                "is_active": True,
                "sold_out": False,
            }
        ]

        result = process_price_table(source_records, target_catalog, profile)

        # Must be marked with blockers
        assert result.has_blockers is True
        dup_issues = [
            i for i in result.issues
            if i.code in ("DUPLICATE_REFERENCE", "BLOCKED_DUPLICATE_REF")
        ]
        assert len(dup_issues) >= 1
        for issue in dup_issues:
            assert issue.severity == IssueSeverity.BLOCKER
            assert "REF-DUP-001" in issue.message or issue.details.get("reference") == "REF-DUP-001"
            # Row numbers or affected indices should be detailed
            assert "rows" in issue.details or issue.row_number is not None

        # Summary must register blocked duplicates
        assert result.summary.blocked_duplicates >= 1
        assert result.summary.updated == 0

        # Existing target catalog item must NOT be updated with arbitrary last value
        target_item = result.output_records[0]
        assert target_item["original_price"] == 50.0
        assert target_item["quantity"] == 5

    def test_duplicate_after_normalization_is_detected(self, profile):
        # Different original representations that normalize to the same key
        source_records = [
            {"REFERENCIA": "sm-a125f/ds", "PRECO": 120.0, "STOCK": 5},
            {"REFERENCIA": "SM-A125FDS", "PRECO": 125.0, "STOCK": 8},
        ]
        target_catalog = []

        result = process_price_table(source_records, target_catalog, profile)

        assert result.has_blockers is True
        dup_issues = [
            i for i in result.issues
            if i.code in ("DUPLICATE_REFERENCE", "BLOCKED_DUPLICATE_REF")
        ]
        assert len(dup_issues) >= 1
        assert dup_issues[0].severity == IssueSeverity.BLOCKER

        # No duplicates should be added into output
        assert len(result.output_records) == 0

    def test_unique_references_are_not_flagged(self, profile):
        source_records = [
            {"REFERENCIA": "REF-001", "PRECO": 10.0, "STOCK": 10},
            {"REFERENCIA": "REF-002", "PRECO": 20.0, "STOCK": 10},
            {"REFERENCIA": "REF-003", "PRECO": 30.0, "STOCK": 10},
        ]
        target_catalog = []

        result = process_price_table(source_records, target_catalog, profile)

        dup_issues = [
            i for i in result.issues
            if i.code in ("DUPLICATE_REFERENCE", "BLOCKED_DUPLICATE_REF")
        ]
        assert len(dup_issues) == 0
        assert result.summary.blocked_duplicates == 0
        assert result.summary.new_added == 3

    def test_triplicate_reference_reports_all_rows(self, profile):
        source_records = [
            {"REFERENCIA": "TRIP-01", "PRECO": 10.0, "STOCK": 10},  # row 1
            {"REFERENCIA": "UNIQUE-01", "PRECO": 20.0, "STOCK": 10}, # row 2
            {"REFERENCIA": "TRIP-01", "PRECO": 12.0, "STOCK": 10},  # row 3
            {"REFERENCIA": "TRIP-01", "PRECO": 15.0, "STOCK": 10},  # row 4
        ]
        target_catalog = []

        result = process_price_table(source_records, target_catalog, profile)
        assert result.has_blockers is True

        dup_issue = next(i for i in result.issues if i.code == "DUPLICATE_REFERENCE")
        assert dup_issue.details["rows"] == [1, 3, 4]
        assert dup_issue.details["count"] == 3
        # The unique item was added, while the triplicate was blocked
        assert result.summary.new_added == 1
        assert len(result.output_records) == 1
        assert result.output_records[0]["internal_identifier"] == "UNIQUE-01"
