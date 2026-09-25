"""Domain models and contracts for Cotarco Commercial Manager.

All models are strictly typed using Pydantic v2 and completely decoupled
from CLI, presentation, database, or external framework concerns.
"""

from __future__ import annotations

from enum import Enum
from typing import Any, Optional
from pydantic import BaseModel, ConfigDict, Field


class IssueSeverity(str, Enum):
    """Severity levels for validation and business rule issues."""
    INFO = "INFO"
    WARNING = "WARNING"
    ERROR = "ERROR"
    BLOCKER = "BLOCKER"


class DecisionCode(str, Enum):
    """Standardized decision outcome codes for item evaluation."""
    UPDATE = "UPDATE"
    NEW_PRODUCT = "NEW_PRODUCT"
    IGNORED_EXISTS = "IGNORED_EXISTS"
    IGNORED_STOCK = "IGNORED_STOCK"
    IGNORED_EMPTY_REF = "IGNORED_EMPTY_REF"
    IGNORED_ZERO_PRICE = "IGNORED_ZERO_PRICE"
    BLOCKED_PRICE_VARIATION = "BLOCKED_PRICE_VARIATION"
    BLOCKED_DUPLICATE_REF = "BLOCKED_DUPLICATE_REF"
    BLOCKED_ZERO_PRICE = "BLOCKED_ZERO_PRICE"
    DUPLICATE_REFERENCE = "DUPLICATE_REFERENCE"
    ZERO_PRICE_REJECTED = "ZERO_PRICE_REJECTED"
    BLOQUEADO_VARIACAO_EXCESSIVA = "BLOQUEADO_VARIACAO_EXCESSIVA"


class PriceRule(BaseModel):
    """Configuration rules for price validation and thresholds."""
    model_config = ConfigDict(extra="ignore")

    max_variation_threshold: float = Field(
        default=0.30,
        ge=0.0,
        description="Maximum accepted price variation threshold before blocking (e.g. 0.30 = 30%).",
    )
    allow_zero_price: bool = Field(
        default=False,
        description="Whether a zero price (0.00) is allowed.",
    )
    reject_negative: bool = Field(
        default=True,
        description="Whether negative prices must be rejected immediately.",
    )


class StockRule(BaseModel):
    """Configuration rules for stock management and product activation."""
    model_config = ConfigDict(extra="ignore")

    min_stock_activation: int = Field(
        default=3,
        ge=0,
        description="Minimum stock count required to activate product (is_active=True, sold_out=False).",
    )
    allow_negative: bool = Field(
        default=False,
        description="Whether negative stock values are allowed.",
    )


class CommercialProfile(BaseModel):
    """Commercial profile defining destination channel settings and rules."""
    model_config = ConfigDict(extra="ignore")

    code: str = Field(
        ...,
        description="Unique identifier code for the profile (e.g. 'MANO', 'WOOCOMMERCE', 'BFA').",
    )
    name: str = Field(
        ...,
        description="Human readable name of the commercial profile.",
    )
    description: Optional[str] = Field(
        default=None,
        description="Detailed description or context of the commercial profile.",
    )
    price_rule: PriceRule = Field(
        default_factory=PriceRule,
        description="Price safety and variation rules.",
    )
    stock_rule: StockRule = Field(
        default_factory=StockRule,
        description="Stock activation and threshold rules.",
    )
    column_mapping: dict[str, list[str]] = Field(
        default_factory=dict,
        description="Mapping of standard domain attributes to file column aliases.",
    )


class Product(BaseModel):
    """Canonical domain product entity representing a commercial catalog item."""
    model_config = ConfigDict(extra="ignore")

    canonical_reference: str = Field(
        ...,
        description="Canonical unique reference code in the internal catalog.",
    )
    original_reference: str = Field(
        ...,
        description="Raw original reference as extracted from supplier or marketplace sheet.",
    )
    normalized_reference: str = Field(
        ...,
        description="Deterministic normalized reference for matching (clean alphanumeric/hyphen).",
    )
    name: Optional[str] = Field(
        default=None,
        description="Product commercial name or designation.",
    )
    brand: Optional[str] = Field(
        default=None,
        description="Brand or manufacturer name.",
    )
    category: Optional[str] = Field(
        default=None,
        description="Category classification.",
    )
    original_price: Optional[float] = Field(
        default=None,
        description="Reference unit price.",
    )
    quantity: Optional[int] = Field(
        default=None,
        description="Available stock quantity.",
    )
    is_active: bool = Field(
        default=True,
        description="Active commercial visibility status.",
    )
    sold_out: bool = Field(
        default=False,
        description="Flag indicating product is sold out.",
    )
    apply_discounted_price: bool = Field(
        default=False,
        description="Flag indicating promotional or discounted pricing applies.",
    )
    extra_data: dict[str, Any] = Field(
        default_factory=dict,
        description="Extensible metadata attributes or custom partner-specific columns.",
    )


class ValidationIssue(BaseModel):
    """Structured issue or violation emitted during validation or processing."""
    model_config = ConfigDict(extra="ignore")

    severity: IssueSeverity = Field(
        ...,
        description="Severity level of the issue (INFO, WARNING, ERROR, BLOCKER).",
    )
    code: str = Field(
        ...,
        description="Machine-readable code identifying the issue type.",
    )
    message: str = Field(
        ...,
        description="Human-readable description of the issue.",
    )
    field: Optional[str] = Field(
        default=None,
        description="Affected field or column name, if applicable.",
    )
    row_number: Optional[int] = Field(
        default=None,
        description="1-based row number in the source file, if applicable.",
    )
    details: dict[str, Any] = Field(
        default_factory=dict,
        description="Contextual details (e.g. previous price, new price, delta).",
    )

    @property
    def is_blocking(self) -> bool:
        """Indicates whether this issue prevents automated execution."""
        return self.severity == IssueSeverity.BLOCKER


class JobItemResult(BaseModel):
    """Detailed evaluation and decision outcome for a single catalog reference item."""
    model_config = ConfigDict(extra="ignore")

    reference_original: str = Field(
        ...,
        description="Original item reference.",
    )
    reference_normalized: str = Field(
        ...,
        description="Normalized item reference used for matching.",
    )
    old_price: Optional[float] = Field(
        default=None,
        description="Previous item price.",
    )
    new_price: Optional[float] = Field(
        default=None,
        description="Proposed new item price.",
    )
    old_stock: Optional[int] = Field(
        default=None,
        description="Previous stock quantity.",
    )
    new_stock: Optional[int] = Field(
        default=None,
        description="Proposed new stock quantity.",
    )
    price_variation_pct: Optional[float] = Field(
        default=None,
        description="Price variation percentage (e.g. 15.5 for +15.5%, -10.0 for -10.0%).",
    )
    decision: str = Field(
        ...,
        description="Human-readable description of the decision.",
    )
    decision_code: DecisionCode | str = Field(
        ...,
        description="Structured decision code from DecisionCode enum.",
    )
    details: dict[str, Any] = Field(
        default_factory=dict,
        description="Supplementary decision metrics or metadata.",
    )


class ProcessSummary(BaseModel):
    """Consolidated quantitative metrics for a catalog processing execution."""
    model_config = ConfigDict(extra="ignore")

    total_source_rows: int = Field(
        default=0,
        ge=0,
        description="Total records inspected from source dataset.",
    )
    total_target_rows: int = Field(
        default=0,
        ge=0,
        description="Total records inspected from target dataset.",
    )
    updated: int = Field(
        default=0,
        ge=0,
        description="Count of existing items successfully updated.",
    )
    new_added: int = Field(
        default=0,
        ge=0,
        description="Count of new items added to catalog.",
    )
    ignored_stock: int = Field(
        default=0,
        ge=0,
        description="Count of items ignored due to insufficient stock threshold.",
    )
    ignored_exists: int = Field(
        default=0,
        ge=0,
        description="Count of items ignored because they already exist in target.",
    )
    ignored_zero_price: int = Field(
        default=0,
        ge=0,
        description="Count of items ignored due to zero price.",
    )
    blocked_price_variation: int = Field(
        default=0,
        ge=0,
        description="Count of items blocked due to price variation exceeding security limit.",
    )
    blocked_duplicates: int = Field(
        default=0,
        ge=0,
        description="Count of items blocked due to duplicate references in source.",
    )
    blocked_zero_price: int = Field(
        default=0,
        ge=0,
        description="Count of items blocked due to zero price violation.",
    )
    total_issues: int = Field(
        default=0,
        ge=0,
        description="Total count of issues detected.",
    )

    @property
    def total_blocked(self) -> int:
        """Total number of blocked items across all blocking rules."""
        return (
            self.blocked_price_variation
            + self.blocked_duplicates
            + self.blocked_zero_price
        )

    @property
    def total_ignored(self) -> int:
        """Total number of ignored items across all ignore conditions."""
        return (
            self.ignored_stock
            + self.ignored_exists
            + self.ignored_zero_price
        )


class ProcessResult(BaseModel):
    """Aggregate processing output containing items, issues, summary, and final records."""
    model_config = ConfigDict(extra="ignore")

    items: list[JobItemResult] = Field(
        default_factory=list,
        description="Individual evaluation outcome for each item.",
    )
    issues: list[ValidationIssue] = Field(
        default_factory=list,
        description="All validation and security issues collected during execution.",
    )
    summary: ProcessSummary = Field(
        default_factory=ProcessSummary,
        description="Consolidated quantitative summary.",
    )
    output_records: list[dict[str, Any]] = Field(
        default_factory=list,
        description="Target dataset records ready for export or persistence.",
    )

    @property
    def has_blockers(self) -> bool:
        """Returns True if any blocker issues exist."""
        return any(issue.severity == IssueSeverity.BLOCKER for issue in self.issues)

    @property
    def total_items(self) -> int:
        """Returns total evaluated items."""
        return len(self.items)
